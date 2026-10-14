import sys,unittest,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import ezdxf
from cad_import import import_dxf

class CADImportTests(unittest.TestCase):
 def test_mm_scale_and_source_bytes_preserved(self):
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder)/'source.dxf';d=ezdxf.new();d.units=4;d.modelspace().add_lwpolyline([(0,0),(9000,0),(9000,3000),(0,3000)],close=True);d.saveas(p);before=p.read_bytes()
   r=import_dxf(str(p));self.assertEqual(p.read_bytes(),before);self.assertEqual(r['qa']['model_to_paper_scale'],.02);self.assertTrue(r['qa']['source_bytes_unchanged']);self.assertLess(r['qa']['maximum_inverse_transform_error_mm'],.00001);self.assertNotIn('<rect fill="#ffffff"',r['svg'])
   a,b=r['segments'][0];self.assertAlmostEqual(abs(b[0]-a[0])*25.4/72,180,places=6)
 def test_non_mm_and_oversize_rejected(self):
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder)/'source.dxf';d=ezdxf.new();d.units=1;d.modelspace().add_line((0,0),(9000,0));d.saveas(p)
   with self.assertRaises(ValueError):import_dxf(str(p))
   d.units=4;d.modelspace().add_line((0,0),(50000,0));d.saveas(p)
   with self.assertRaises(ValueError):import_dxf(str(p))

if __name__=='__main__':unittest.main()
