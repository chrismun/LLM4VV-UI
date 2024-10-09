import re
import json

def parse_toc(toc):
    # Extract headings from the table of contents
    headings = re.findall(r'(\d+(?:\.\d+)*)(?:\s+)([^\n]+)', toc)
    return headings

def split_by_toc(file_path, toc):
    headings = parse_toc(toc)
    chunks = {}
    current_heading = None
    buffer = ""

    with open(file_path, 'r') as file:
        for line in file:
            # Check if the line matches any heading
            match = re.match(r'(\d+(?:\.\d+)*)\s+(.*)', line)
            if match:
                heading_number, heading_text = match.groups()
                # If the current heading is not None, store the buffer to the chunks
                if current_heading:
                    chunks[current_heading] = buffer.strip()
                    buffer = ""
                # Check if the heading text matches with the TOC
                for h_number, h_text in headings:
                    if heading_number == h_number and heading_text.strip() == h_text.strip():
                        current_heading =  heading_number + " " + heading_text
                        break
            buffer += line

        # Store the last chunk
        if current_heading:
            chunks[current_heading] = buffer.strip()

    return chunks

mapping = {
    "parallel construct": "251 Parallel Construct",
    "serial construct": "252 Serial Construct",
    "kernels construct": "253 Kernels Construct",
    "compute construct if clause": "256 if clause",
    "compute construct self clause": "257 self clause",
    "compute construct async clause": "258 async clause",
    "compute construct wait clause": "259 wait clause",
    "compute construct num_gangs clause": "2510 num gangs clause",
    "compute construct num_workersclause": "2511 num workers clause",
    "compute construct vector_length clause": "2512 vector length clause",
    "compute construct private clause": "2513 private clause",
    "compute construct firstprivate clause": "2514 ﬁrstprivate clause",
    "compute construct reduction clause": "2515 reduction clause",
    "compute construct default clause": "2516 default clause",
    "variable predetermined data attributes": "261 Variables with Predetermined Data Attributes",
    "variable implicit data attributes": "262 Variables with Implicitly Determined Data Attributes",
    "data construct": "265 Data Construct",
    "reference counters": "267 Reference Counters",
    "attachment counter": "268 Attachment Counter",
    "data deviceptr clause": "274 deviceptr clause",
    "data present clause": "275 present clause",
    "data construct copy clause": "276 copy clause",
    "data construct copyin clause": "277 copyin clause",
    "data construct copyout clause": "278 copyout clause",
    "data construct create clause": "279 create clause",
    "data construct no_create clause": "2710 no create clause",
    "data construct delete clause": "2711 delete clause",
    "data construct attach clause": "2712 attach clause",
    "data construct detach clause": "2713 detach clause",
    "host_data construct use_device clause": "281 use device clause",
    "host_data construct if clause": "282 if clause",
    "host_data construct if_present clause": "283 if present clause",
    "loop construct collapse clause": "291 collapse clause",
    "loop construct gang clause": "292 gang clause",
    "loop construct worker clause": "293 worker clause",
    "loop construct vector clause": "294 vector clause",
    "loop construct seq clause": "295 seq clause",
    "loop construct independent clause": "296 independent clause",
    "loop construct auto clause": "297 auto clause",
    "loop construct tile clause": "298 tile clause",
    "loop construct device_type clause": "299 device type clause",
    "loop construct private clause": "2910 private clause",
    "loop construct reduction clause": "2911 reduction clause",
    "cache directive": "210 Cache Directive",
    "combined constucts": "211 Combined Constructs",
    "atomic construct": "212 Atomic Construct",
    "declare directive": "213 Declare Directive",
    "declare directive device_resident clause": "2131 device resident clause",
    "declare directive create clause": "2132 create clause",
    "declare directive link clause": "2133 link clause",
    "init directive": "2141 Init Directive",
    "shutdown directive": "2142 Shutdown Directive",
    "set directive": "2143 Set Directive",
    "update directive": "2144 Update Directive",
    "wait directive": "2145 Wait Directive",
    "enter data directive": "2146 Enter Data Directive",
    "exit data directive": "2147 Exit Data Directive",
    "routine directive": "2151 Routine Directive",
    "async clause": "2161 async clause",
    "wait clause": "2162 wait clause",
    "wait directive": "2163 Wait Directive",
    "acc get num devices": "321 acc getnum devices",
    "acc set device type": "322 acc setdevice type",
    "acc get device type": "323 acc getdevice type",
    "acc set device num": "324 acc setdevice num",
    "acc get device num": "325 acc getdevice num",
    "acc get property": "326 acc getproperty",
    "acc init": "327 acc init",
    "acc shutdown": "328 acc shutdown",
    "acc async test": "329 acc async test",
    "acc wait": "3210 acc wait",
    "acc wait async": "3211 acc wait async",
    "acc wait any": "3212 acc wait any",
    "acc get default async": "3213 acc getdefault async",
    "acc set default async": "3214 acc setdefault async",
    "acc on device": "3215 acc ondevice",
    "acc malloc": "3216 acc malloc",
    "acc free": "3217 acc free",
    "acc copyin and acc create": "3218 acc copyin and acc create",
    "acc copyout and acc delete": "3219 acc copyout and acc delete",
    "acc update device and acc update self": "3220 acc update device and acc update self",
    "acc map data": "3221 acc map data",
    "acc unmap data": "3222 acc unmap data",
    "acc deviceptr": "3223 acc deviceptr",
    "acc hostptr": "3224 acc hostptr",
    "acc is present": "3225 acc ispresent",
    "acc memcpy to device": "3226 acc memcpy todevice",
    "acc memcpy from device": "3227 acc memcpy from device",
    "acc memcpy device": "3228 acc memcpy device",
    "acc attach and acc detach": "3229 acc attach and acc detach",
    "acc memcpy d2d": "3230 acc memcpy d2d"
}




# Extract content based on the mapping
file_path = "spec.txt"
toc = """1 Introduction
11 Scope                                         
12 Execution Model                                   
13 Memory Model                                    
14 Language Interoperability                               
15 Runtime Errors                                    
16 Conventions used in this document                          
17 Organization of this document                            
18 References                                       
19 Changes from Version 10 to 20                           
110 Corrections in the August 2013 document                      
111 Changes from Version 20 to 25                           
112 Changes from Version 25 to 26                           
113 Changes from Version 26 to 27                           
114 Changes from Version 27 to 30                           
115 Changes from Version 30 to 31                           
116 Changes from Version 31 to 32                           
117 Changes from Version 32 to 33                           
118 Topics Deferred For a Future Revision                        
2 Directives
21 Directive Format                                   
22 Conditional Compilation                               
23 Internal Control Variables                               
231 Modifying and Retrieving ICV Values                    
24 Device-Speciﬁc Clauses                               
25 Compute Constructs                                  
251 Parallel Construct                               
252 Serial Construct                                
253 Kernels Construct                               
254 Compute Construct Restrictions                       
255 Compute Construct Errors                          
256 if clause                                    
257 self clause                                   
258 async clause                                 
259 wait clause                                  
2510 num gangs clause                               
2511 num workers clause                             
2512 vector length clause                             
2513 private clause                                 
2514 ﬁrstprivate clause                               
2515 reduction clause                               
2516 default clause                                 

26 Data Environment                                   
261 Variables with Predetermined Data Attributes                
262 Variables with Implicitly Determined Data Attributes            
263 Data Regions and Data Lifetimes                      
264 Data Structures with Pointers                         
265 Data Construct                                
266 Enter Data and Exit Data Directives                     
267 Reference Counters                              
268 Attachment Counter                             
27 Data Clauses                                     
271 Data Speciﬁcation in Data Clauses                      
272 Data Clause Actions                             
273 Data Clause Errors                              
274 deviceptr clause                                
275 present clause                                 
276 copy clause                                  
277 copyin clause                                 
278 copyout clause                                
279 create clause                                 
2710 no create clause                                
2711 delete clause                                 
2712 attach clause                                 
2713 detach clause                                 
28 Host Data Construct                                 
281 use device clause                               
282 if clause                                    
283 if present clause                               
29 Loop Construct                                    
291 collapse clause                                
292 gang clause                                  
293 worker clause                                 
294 vector clause                                 
295 seq clause                                   
296 independent clause                              
297 auto clause                                  
298 tile clause                                   
299 device type clause                              
2910 private clause                                 
2911 reduction clause                               
210 Cache Directive                                    
211 Combined Constructs                                 
212 Atomic Construct                                   
213 Declare Directive                                   
2131 device resident clause                            
2132 create clause                                 
2133 link clause                                  
214 Executable Directives                                 
2141 Init Directive                                 

2142 Shutdown Directive                              
2143 Set Directive                                 
2144 Update Directive                               
2145 Wait Directive                                
2146 Enter Data Directive                             
2147 Exit Data Directive                              
215 Procedure Calls in Compute Regions                         
2151 Routine Directive                               
2152 Global Data Access                              
216 Asynchronous Behavior                                
2161 async clause                                 
2162 wait clause                                  
2163 Wait Directive                                
217 Fortran Speciﬁc Behavior                               
2171 Optional Arguments                             
2172 Do Concurrent Construct                           
3 Runtime Library
31 Runtime Library Deﬁnitions                             
32 Runtime Library Routines                              
321 acc getnum devices                             
322 acc setdevice type                              
323 acc getdevice type                              
324 acc setdevice num                              
325 acc getdevice num                              
326 acc getproperty                               
327 acc init                                    
328 acc shutdown                                 
329 acc async test                                 
3210 acc wait                                    
3211 acc wait async                                
3212 acc wait any                                 
3213 acc getdefault async                             
3214 acc setdefault async                             
3215 acc ondevice                                 
3216 acc malloc                                  
3217 acc free                                    
3218 acc copyin and acc create                          
3219 acc copyout and acc delete                          
3220 acc update device and acc update self                    
3221 acc map data                                 
3222 acc unmap data                                
3223 acc deviceptr                                 
3224 acc hostptr                                  
3225 acc ispresent                                 
3226 acc memcpy todevice                            
3227 acc memcpy from device                          
3228 acc memcpy device                             

3229 acc attach and acc detach                          
3230 acc memcpy d2d                               
4 Environment Variables
41 ACC DEVICE TYPE                                 
42 ACC DEVICE NUM                                 
43 ACC PROFLIB                                    
5 Proﬁling and Error Callback Interface
51 Events                                         
511 Runtime Initialization and Shutdown                    
512 Device Initialization and Shutdown                     
513 Enter Data and Exit Data                           
514 Data Allocation                                
515 Data Construct                                
516 Update Directive                               
517 Compute Construct                              
518 Enqueue Kernel Launch                           
519 Enqueue Data Update (Upload and Download)               
5110 Wait                                      
5111 Error Event                                  
52 Callbacks Signature                                  
521 First Argument: General Information                    
522 Second Argument: Event-Speciﬁc Information               
523 Third Argument: API-Speciﬁc Information                 
53 Loading the Library                                  
531 Library Registration                             
532 Statically-Linked Library Initialization                   
533 Runtime Dynamic Library Loading                     
534 Preloading with LD PRELOAD                       
535 Application-Controlled Initialization                     
54 Registering Event Callbacks                             
541 Event Registration and Unregistration                    
542 Disabling and Enabling Callbacks                      
55 Advanced Topics                                   
551 Dynamic Behavior                              
552 OpenACC Events During Event Processing                 
553 Multiple Host Threads                            
6 Glossary
A Recommendations for Implementers
A1 Target Devices                                    
A11 NVIDIA GPU Targets                            
A12 AMD GPU Targets                              
A13 Multicore Host CPU Target                         
A2 API Routines for Target Platforms                          
A21 NVIDIA CUDA Platform                          

A22 OpenCL Target Platform                           
A3 Recommended Options and Diagnostics                       
A31 C Pointer in Present clause                          
A32 Nonconforming Applications and Implementations             
A33 Automatic Data Attributes                          
A34 Routine Directive with a Name                        
"""
chunks = split_by_toc(file_path, toc)

chunks = split_by_toc(file_path, toc)
for heading, content in chunks.items():
    print(f"--- {heading} ---")
    print(content)
    print("\n\n")


dataset = {}
for feature, heading in mapping.items():
    dataset[feature] = chunks.get(heading, "")

with open("dataset.json", "w") as json_file:
    json.dump(dataset, json_file, indent=4)

print("Dataset saved to dataset.json")
