# AI-Powered-Call-Center-Local-Deploy:FreeSWITCH+Java+SpringBoot+VUE
AI-enhanced call center system, based on FreeSWITCH, Java, Python, SpringBoot, VUE and other technology stacks, can be connected to mainstream TTS, ASR products, can be deployed locally, can build automatic outbound call system, automatic inbound call robot system, agent assistance system;Can work with online customer service and work order system to realize unified queuing of text messages and voice calls.

# 😄 We firmly believe that only when the software is used can it bring value to users and allow itself to iterate!
# 😄Sustainability: It has been continuously iterating since 2014, and the members are very experienced and long-term!
# Our goal
Committed to becoming: a global leader in large-model call center systems, large-model inbound robots, large-model outbound robots, and intelligent call center systems! ! !
# Features List

## Connect with telephone operator

1. Gateway management: Connect to the operator's voice gateway for incoming and outgoing calls
2. Gateway registration: Voice gateway registration
3. Gateway multiple lines: Currently, the main connections are T1 (30B+D) lines, SIP lines, FXO analog lines, or other PBX third-party devices that support SIP.
4. Blacklist: Add certain incoming call numbers to the blacklist

## Call center incoming call function

1. Call routing mode: Select the gateway and line for routing according to the dialing plan
2. Caller-based routing: Routing according to the caller's number
3. Callee-based routing: Routing according to the called number
4. DTMF-based routing: Routing according to DTMF
5. ASR-based routing:	ASR identifies the user selection for routing
6. Database interaction-based routing: Call processing and routing based on the collected information through database interaction
7. Skill group-based routing: Routing by skill group
8. Priority-based routing：Routing according to user priority
9. Secondary routing：Perform secondary new routing based on a certain number of queues
10. Time-based routing: Routing based on time (time of day), date (day of week) and holidays
11. IVR voice files: Welcome message files, etc.
12. TTS: Welcome message files can be intelligently broadcasted through TTS
13. ASR:Support user ASR recognition into text information
14. IVR editing:	IVR visual process editing, support menu, time and date, HTTP interface, voice broadcast, route selection, assignment, conditional judgment, intelligent dialogue, DTMF collection, hang up and end
Agent selection strategy	Agent selection strategy: longest waiting time, longest average waiting time, minimum number of answered calls, shortest call time, random selection, etc.
15. Agent call connection:	Agent general functions: sign in, sign out, busy, ready, hang up, outbound call
16. Agent name notification: function	Hear the agent's name prompt when transferring the call
17. Multi-party conference:	Support multi-party conference
18. Team leader function:	Monitor, force insertion, and force removal
19. Real-time voice stream push: Support push of call voice stream to third party
20. Call mute:	Mute the agent
21. Call hold:	The agent holds the call
22. Call transfer:	The agent transfers the call to other agents, queues, external lines, etc.
23. Call consultation:	The agent consults other agents and resumes the call
24. Call status push:	Push the call status
25. Incoming call pop-up screen:	Monitor incoming call messages, pop up the browser screen, and bring out the required information
26. Recording:	Supports WAV, MP3, dual-track recording, supports recording upload
27. Satisfaction evaluation:	Supports satisfaction evaluation
28. Inbound call report: Detailed call report

## Call out function
1. Predictive outbound calls:	After the user is connected, he/she will be transferred to an idle seat
2. Outbound call tasks:	Creation and deletion of outbound call tasks
3. Outbound call strategies:	Setting outbound call strategies: outbound call time, re-call strategy, outbound call script settings
4. Outbound call data sources:	Data source association with outbound call data
5. Outbound call monitoring:	Outbound call task monitoring
6. Outbound call reports:	Outbound call report data
7. Call details:	Call details (incoming/outgoing call time, queue entry time, main/called ringing time, answering time, hang-up time, recording time, call duration, call duration, etc.)
8. Call bill push:	Pushing call records to third-party systems

## AI intelligent functions
1. Intelligent knowledge base:	Support document, QA import, document vectorization, full-text search, vector search, dynamic addition of related questions
2. AI Agent intelligent process:	Support advanced visual process arrangement, can be based on actual business, each intelligent node flow, support priority knowledge base search, and then optimize the output of the large model
3. Intelligent inbound and outbound: IVR	Call IVR, support access to intelligent digital employees, docking with large models, dynamic IVR, intelligent flow, support HTTP method, access to third-party large model NLP
4. Online customer service:	H5 online customer service (supports intelligent Q&A through background knowledge base and large model)

## Report functions
1. Agent status table:	Record agent login, idle, busy, answering, outbound calls, etc.
2. Agent statistics report:	Query agent statistics by time
3. Outbound call task status:	View outbound call task status
4. Queue status:	View queue status

## Management function
1. User management:	Management of user accounts used to log into the system
2. Phone management:	IP extension phones registered in the system
3. Directory number management:	Extension number management
4. Menu management:	System menu management, different roles have different permissions to view different menu options
5. Role management:	User permission roles
6. Number pool management:	Multiple number collections
7. Skill group management:	Service attribute-related seat capability groups, with multiple seats in the group
8. Agent management:	Agent management
9. Skills:	Skills related to business attributes

## API function
1. CTI interface:	Sign in, sign out, busy, idle, after the call, answer, hang up, outgoing, consultation, transfer, forced insertion, forced removal, monitoring
2. Outbound call data import:	Batch import, outbound call data, mainly import outbound call numbers, outbound call items
3. Call record push:	Push real-time data after hanging up (incoming/outgoing call time, queue time, main/called ringing time, answer time, hang up time, recording time, call duration, call duration, etc.)
## Others
1. Cluster management:	Support FreeSWITCH cluster
2. Multi-database support:	MySQL、PostgreSQL、SQLServer、Oracle!

# Features List screenshot
![image](https://github.com/user-attachments/assets/a6fd5d47-f2d9-407a-9d04-9be583d4c6de)
![image](https://github.com/user-attachments/assets/a71260b4-9e13-474b-ae86-c867dc396ac1)
![image](https://github.com/user-attachments/assets/63659ce3-b3f7-4055-a125-4a26ef8deb6d)
![image](https://github.com/user-attachments/assets/ac90112f-311d-4ebb-8206-dff3ae643ee9)




   
