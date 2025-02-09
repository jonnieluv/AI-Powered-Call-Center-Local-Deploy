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
Caller-based routing	Routing according to the caller's number
Callee-based routing	Routing according to the called number
DTMF-based routing	Routing according to DTMF
ASR-based routing	ASR identifies the user selection for routing
Database interaction-based routing	Call processing and routing based on the collected information through database interaction
Skill group-based routing	Routing by skill group
Priority-based routing	Routing according to user priority
Secondary routing	Perform secondary new routing based on a certain number of queues
Time-based routing	Routing based on time (time of day), date (day of week) and holidays
IVR voice files	Welcome message files, etc.
TTS	Welcome message files can be intelligently broadcasted through TTS
ASR	Support user ASR recognition into text information
IVR editing	IVR visual process editing, support menu, time and date, HTTP interface, voice broadcast, route selection, assignment, conditional judgment, intelligent dialogue, DTMF collection, hang up and end
Agent selection strategy	Agent selection strategy: longest waiting time, longest average waiting time, minimum number of answered calls, shortest call time, random selection, etc.
Agent call connection	Agent general functions: sign in, sign out, busy, ready, hang up, outbound call
Agent name notification function	Hear the agent's name prompt when transferring the call
Multi-party conference	Support multi-party conference
Team leader function	Monitor, force insertion, and force removal
Real-time voice stream push	Support push of call voice stream to third party
Call mute	Mute the agent
Call hold	The agent holds the call
Call transfer	The agent transfers the call to other agents, queues, external lines, etc.
Call consultation	The agent consults other agents and resumes the call
Call status push	Push the call status
Incoming call pop-up screen	Monitor incoming call messages, pop up the browser screen, and bring out the required information
Recording	Supports WAV, MP3, dual-track recording, supports recording upload
Satisfaction evaluation	Supports satisfaction evaluation
Inbound call report	Detailed call report
Predictive outbound calls	After the user is connected, he/she will be transferred to an idle seat
Outbound call tasks	Creation and deletion of outbound call tasks
Outbound call strategies	Setting outbound call strategies: outbound call time, re-call strategy, outbound call script settings
Outbound call data sources	Data source association with outbound call data
Outbound call monitoring	Outbound call task monitoring
Outbound call reports	Outbound call report data
Call details	Call details (incoming/outgoing call time, queue entry time, main/called ringing time, answering time, hang-up time, recording time, call duration, call duration, etc.)
Call bill push	Pushing call records to third-party systems
Intelligent knowledge base	Support document, QA import, document vectorization, full-text search, vector search, dynamic addition of related questions
AI Agent intelligent process	Support advanced visual process arrangement, can be based on actual business, each intelligent node flow, support priority knowledge base search, and then optimize the output of the large model
Intelligent inbound and outbound IVR	Call IVR, support access to intelligent digital employees, docking with large models, dynamic IVR, intelligent flow, support HTTP method, access to third-party large model NLP
Online customer service	H5 online customer service (supports intelligent Q&A through background knowledge base and large model)
Agent status table	Record agent login, idle, busy, answering, outbound calls, etc.
Agent statistics report	Query agent statistics by time
Outbound call task status	View outbound call task status
Queue status	View queue status
User management	Management of user accounts used to log into the system
Phone management	IP extension phones registered in the system
Directory number management	Extension number management
Menu management	System menu management, different roles have different permissions to view different menu options
Role management	User permission roles
Number pool management	Multiple number collections
Skill group management	Service attribute-related seat capability groups, with multiple seats in the group
Agent management	Agent management
Skills	Skills related to business attributes
CTI interface	Sign in, sign out, busy, idle, after the call, answer, hang up, outgoing, consultation, transfer, forced insertion, forced removal, monitoring
Outbound call data import	Batch import, outbound call data, mainly import outbound call numbers, outbound call items
Call record push	Push real-time data after hanging up (incoming/outgoing call time, queue time, main/called ringing time, answer time, hang up time, recording time, call duration, call duration, etc.)
Cluster management	Support FreeSWITCH cluster
Multi-database support	MySQL、PostgreSQL、SQLServer、Oracle![image](https://github.com/user-attachments/assets/41bd6de8-5695-4866-a2f3-12d4941e5eb5)
