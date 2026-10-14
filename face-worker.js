import {detectFaces} from './geometry.js';
self.onmessage=e=>{try{self.postMessage({faces:detectFaces(e.data)});}catch(error){self.postMessage({error:error.message});}};
