export function orderedIds(assignments,order=[]){
 const ids=Object.keys(assignments).map(Number),valid=new Set(ids),seen=new Set(),result=[];
 for(const id of order)if(valid.has(id)&&!seen.has(id)){result.push(id);seen.add(id);}
 return [...result,...ids.filter(id=>!seen.has(id))];
}
export function paintRuns(faces,assignments,order=[],sizes={}){
 const byId=new Map(faces.map(f=>[f.id,f])),runs=[];
 for(const id of orderedIds(assignments,order)){const face=byId.get(id);if(!face)continue;const kind=assignments[id],size=sizes[id]??1,last=runs.at(-1);if(last&&last.kind===kind&&last.size===size&&!face.exclusions?.length&&!last.faces.some(f=>f.exclusions?.length))last.faces.push(face);else runs.push({kind,size,faces:[face]});}
 return runs;
}
export function moveLayer(assignments,order,id,direction){
 const result=orderedIds(assignments,order),index=result.indexOf(id);if(index<0)return result;result.splice(index,1);
 const next=direction==='front'?result.length:direction==='back'?0:Math.max(0,Math.min(result.length,index+(direction==='up'?1:-1)));result.splice(next,0,id);return result;
}
