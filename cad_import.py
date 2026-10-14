"""Runs locally or in Pyodide; imports millimetre DXF without saving it."""
import json,hashlib,math,re
from pathlib import Path
import ezdxf
from ezdxf.addons.drawing import svg,layout,Frontend,RenderContext
from ezdxf.addons.drawing.config import Configuration,HatchPolicy,BackgroundPolicy
from ezdxf import bbox

class PaperFitError(ValueError):
 def __init__(self,width,height,scale):
  required=max(width/400,height/277)
  self.suggested_scale=next((s for s in (20,50,100,200,500,1000,2000,5000,10000) if s>=required),math.ceil(required))
  super().__init__(f"Drawing is {width:,.0f} × {height:,.0f} mm and will not fit A3 at 1:{scale}. Try 1:{self.suggested_scale}. CAD geometry remains unchanged.")

def import_dxf(path,denominator=50):
 original=Path(path).read_bytes();doc=ezdxf.readfile(path)
 if doc.units!=4:raise ValueError('DXF must explicitly use millimetres ($INSUNITS=4).')
 ext=bbox.extents(doc.modelspace(),fast=False)
 if not ext.has_data:raise ValueError('No measurable model-space geometry.')
 if abs(ext.extmin.z)>1e-8 or abs(ext.extmax.z)>1e-8:raise ValueError('Only 2D model-space plans/elevations at Z=0 are supported.')
 backend=svg.SVGBackend();Frontend(RenderContext(doc),backend,config=Configuration(hatch_policy=HatchPolicy.SHOW_OUTLINE,background_policy=BackgroundPolicy.WHITE)).draw_layout(doc.modelspace())
 box=backend.player().bbox()
 if box.size.x/denominator>400 or box.size.y/denominator>277:raise PaperFitError(box.size.x,box.size.y,denominator)
 source_svg=backend.get_string(layout.Page(420,297,layout.Units.mm,margins=layout.Margins.all(10)),settings=layout.Settings(scale=1/denominator,fit_page=False,output_coordinate_space=10000000,crop_at_margins=False))
 # Remove only the SVG backend's synthetic paper background, not CAD fills.
 source_svg=re.sub(r'<rect fill="#ffffff" x="0" y="0" width="10000000" height="7071429" fill-opacity="1.0" />','',source_svg,count=1)
 matrix=backend.transformation_matrix;factor=420/10000000*72/25.4
 def point(p):
  q=matrix.transform((p[0],p[1],0));return [q.x*factor,q.y*factor]
 segments=[];notes=[];dimensions=[];curves=[];controls=[]
 for e in doc.modelspace():
  typ=e.dxftype()
  if typ=='LINE':
   segments.append([point(e.dxf.start),point(e.dxf.end)]);controls.extend([tuple(e.dxf.start),tuple(e.dxf.end)])
  elif typ=='LWPOLYLINE':
   if e.has_arc:curves.append(e.dxf.handle);continue
   ps=list(e.vertices_in_wcs());controls.extend(tuple(p) for p in ps)
   if e.closed and ps:ps.append(ps[0])
   segments.extend([point(a),point(b)] for a,b in zip(ps,ps[1:]))
  elif typ=='TEXT':notes.append(e.dxf.text)
  elif typ=='MTEXT':notes.append(e.plain_text())
  elif typ=='DIMENSION':
   try:m=e.get_measurement();m=list(m) if hasattr(m,'__iter__') else m
   except Exception:m='Unavailable'
   dimensions.append({'handle':e.dxf.handle,'measurement_mm':m})
  elif typ in ('ARC','CIRCLE','SPLINE','ELLIPSE','INSERT'):curves.append(e.dxf.handle)
 errors=[];inverse=matrix.copy();inverse.inverse()
 for p in controls:
  q=inverse.transform(matrix.transform(p));errors.append(math.dist(p,tuple(q)))
 return {'svg':source_svg,'width':420*72/25.4,'height':297*72/25.4,'segments':segments,'notes':'\n'.join(notes),'scale':denominator,
  'qa':{'source_sha256':hashlib.sha256(original).hexdigest(),'source_bytes_unchanged':original==Path(path).read_bytes(),
    'model_space_units':'millimetres','model_to_paper_scale':1/denominator,'auto_fit':False,'dimensions':dimensions,
    'model_extents_mm':[list(ext.extmin),list(ext.extmax)],'control_points_checked':len(controls),'maximum_inverse_transform_error_mm':max(errors,default=0),
    'svg_rounding_bound_model_mm':math.sqrt(2)*.5*420/10000000*denominator,
    'review_items':['Curved, block and non-top-level boundaries are not automatically assigned: '+','.join(curves)] if curves else [],
    'limitations':['Original CAD fonts may differ from available browser/Python fonts. Curves use the CAD library SVG representation. Model-space DXF is placed on a new A3 sheet; existing DXF paperspace title blocks require the desktop renderer.']}}
