"""
Management command: seed_interview_questions
---------------------------------------------
Populates InterviewGuard with a rich set of approved interview
questions and approved CV builder recommendations.

Usage:
    python manage.py seed_interview_questions           # insert only (skip duplicates)
    python manage.py seed_interview_questions --flush   # delete all existing first
"""

from django.core.management.base import BaseCommand
from core.models import CVBuilder, InterviewQuestion


CV_BUILDERS = [
    {
        "name": "Zety",
        "short_description": "Professional resume templates with guided writing help and examples.",
        "link": "https://zety.com",
        "order": 1,
    },
    {
        "name": "Novoresume",
        "short_description": "Clean, ATS-friendly CV layouts for students and early-career applicants.",
        "link": "https://novoresume.com",
        "order": 2,
    },
    {
        "name": "Canva Resumes",
        "short_description": "Visual resume templates that are easy to edit and export.",
        "link": "https://canva.com/resumes",
        "order": 3,
    },
    {
        "name": "Reactive Resume",
        "short_description": "Free, open-source resume builder with developer-friendly exports.",
        "link": "https://rxresu.me",
        "order": 4,
    },
]


QUESTIONS = [

    # ─── GENERAL (ALL FACULTIES) ────────────────────────────────────────────

    dict(faculty="general", difficulty="beginner", order=1,
         question="Tell me about yourself.",
         answer=(
             "Give a concise 60-90 second pitch: who you are, what you study, "
             "relevant experience or projects, and why you are excited about this "
             "attachment. Keep it professional and end by linking your background "
             "to the role you are applying for."
         ),
         tip="The interviewer wants to see communication skills and self-awareness. "
             "Avoid reciting your CV word-for-word.",
         tags="introduction, communication, self-awareness"),

    dict(faculty="general", difficulty="beginner", order=2,
         question="Why do you want to do your industrial attachment at this company?",
         answer=(
             "Research the company beforehand. Mention specific products, services, "
             "or values that align with your goals. Show that you have thought about "
             "how working there will help you grow and what value you can bring."
         ),
         tip="Generic answers ('I want to gain experience') are red flags. "
             "Be specific about the company.",
         tags="motivation, research, company fit"),

    dict(faculty="general", difficulty="beginner", order=3,
         question="What are your strengths and weaknesses?",
         answer=(
             "Strengths: choose 2-3 that are relevant to the role and back each with "
             "a brief example. Weaknesses: pick a genuine one, then explain the steps "
             "you are actively taking to improve it. Avoid clichés like 'I work too hard'."
         ),
         tip="Honesty and self-awareness score more than a polished lie.",
         tags="self-awareness, strengths, weaknesses"),

    dict(faculty="general", difficulty="beginner", order=4,
         question="Where do you see yourself in five years?",
         answer=(
             "Be honest but ambitious. Connect your answer to growth in your field—"
             "e.g., becoming a mid-level software developer, leading a small team, "
             "or specialising in a specific domain. Show you have direction."
         ),
         tip="Interviewers want to see ambition and stability, not that you see "
             "this attachment as a stepping-stone to leave immediately.",
         tags="career goals, ambition"),

    dict(faculty="general", difficulty="intermediate", order=5,
         question="Describe a time you faced a challenge and how you handled it.",
         answer=(
             "Use the STAR method: Situation, Task, Action, Result. "
             "Pick a real academic or personal challenge. Focus on the actions YOU took "
             "and what you learned. Keep it relevant—a technical challenge is best for "
             "a tech role."
         ),
         tip="Prepare 2-3 STAR stories before any interview.",
         tags="problem-solving, STAR, resilience"),

    dict(faculty="general", difficulty="beginner", order=6,
         question="Are you comfortable working in a team?",
         answer=(
             "Yes—give a concrete example: a group project, hackathon, or club activity "
             "where you collaborated effectively. Mention your role and the outcome."
         ),
         tip="Back every claim with a real example.",
         tags="teamwork, collaboration"),

    dict(faculty="general", difficulty="beginner", order=7,
         question="How do you manage your time when you have multiple deadlines?",
         answer=(
             "Describe your system: you might use a task manager (Trello, Notion), "
             "prioritise by urgency and importance (Eisenhower matrix), break tasks "
             "into smaller steps, and communicate early if a deadline is at risk."
         ),
         tip="Mention a real situation where this helped you deliver on time.",
         tags="time management, organisation, productivity"),

    dict(faculty="general", difficulty="beginner", order=8,
         question="What do you know about our industry?",
         answer=(
             "Research current trends, challenges, and key players. For Zimbabwe, "
             "mention relevant local context—e.g., digital transformation, fintech growth, "
             "or specific challenges the sector faces locally."
         ),
         tip="Reading recent news articles about the company or sector the day before "
             "will set you apart.",
         tags="industry knowledge, research"),

    dict(faculty="general", difficulty="intermediate", order=9,
         question="How do you handle feedback or criticism?",
         answer=(
             "Explain that you welcome constructive feedback as a tool for growth. "
             "Give an example where feedback led you to improve—perhaps a lecturer's "
             "comment on an assignment or a code review from a peer."
         ),
         tip="Never say you don't need feedback or that you handle it 'fine'. "
             "Show the growth mindset.",
         tags="feedback, growth mindset, communication"),

    dict(faculty="general", difficulty="beginner", order=10,
         question="Do you have any questions for us?",
         answer=(
             "Always have 2-3 questions ready. Good ones: 'What does a typical day "
             "look like for an attachment student here?', 'What tools or technologies "
             "will I be working with?', 'How is performance feedback given?'"
         ),
         tip="Asking nothing signals lack of interest. Never ask about salary first.",
         tags="questions, engagement, curiosity"),

    # ─── COMPUTER SCIENCE ───────────────────────────────────────────────────

    dict(faculty="computer_science", difficulty="beginner", order=1,
         question="What programming languages are you proficient in?",
         answer=(
             "List languages you have actually used in projects or coursework. "
             "Rate your proficiency honestly (beginner / intermediate / advanced). "
             "Mention the context: e.g., 'Python for data structures assignments and a "
             "personal web scraping project; JavaScript for a front-end project in "
             "second year.'"
         ),
         tip="Honesty beats exaggeration. Interviewers often give a quick coding test.",
         tags="Python, Java, JavaScript, languages, proficiency"),

    dict(faculty="computer_science", difficulty="beginner", order=2,
         question="Explain the difference between a stack and a queue.",
         answer=(
             "A stack is Last-In-First-Out (LIFO): the last element added is the first "
             "removed—like a stack of plates. A queue is First-In-First-Out (FIFO): "
             "the first element added is the first removed—like people waiting in a line. "
             "Stacks are used in function call management and undo operations; queues in "
             "task scheduling and breadth-first search."
         ),
         tip="Draw it out mentally and give a real-world analogy.",
         tags="data structures, stack, queue, LIFO, FIFO"),

    dict(faculty="computer_science", difficulty="beginner", order=3,
         question="What is the difference between an array and a linked list?",
         answer=(
             "An array stores elements in contiguous memory; access is O(1) by index "
             "but insertion/deletion in the middle is O(n). A linked list stores nodes "
             "with pointers to the next node; insertion/deletion is O(1) if you have the "
             "node reference, but access is O(n) because you must traverse from the head."
         ),
         tip="Know Big-O for basic operations on both.",
         tags="data structures, array, linked list, Big-O"),

    dict(faculty="computer_science", difficulty="intermediate", order=4,
         question="What is Object-Oriented Programming? Explain its four pillars.",
         answer=(
             "OOP is a paradigm where code is organised around objects that combine "
             "state (data) and behaviour (methods). The four pillars are: "
             "1) Encapsulation – bundling data and methods, hiding internal state. "
             "2) Inheritance – a class deriving properties from a parent class. "
             "3) Polymorphism – the same interface behaving differently based on context. "
             "4) Abstraction – exposing only essential details, hiding complexity."
         ),
         tip="Be ready to write a small code example illustrating each pillar.",
         tags="OOP, encapsulation, inheritance, polymorphism, abstraction"),

    dict(faculty="computer_science", difficulty="beginner", order=5,
         question="What is version control and why is it important?",
         answer=(
             "Version control tracks changes to code over time, letting you revert to "
             "earlier versions, collaborate without overwriting each other's work, and "
             "maintain a history of who changed what and why. Git is the most widely used "
             "system; GitHub, GitLab, and Bitbucket are popular hosting platforms."
         ),
         tip="Know the basic Git workflow: clone, branch, commit, push, pull request.",
         tags="Git, version control, collaboration, GitHub"),

    dict(faculty="computer_science", difficulty="beginner", order=6,
         question="What is the difference between HTTP and HTTPS?",
         answer=(
             "HTTP (HyperText Transfer Protocol) transmits data in plain text. "
             "HTTPS is HTTP with TLS/SSL encryption, so data in transit is scrambled "
             "and cannot be read by eavesdroppers. HTTPS also verifies the server's "
             "identity via certificates, protecting against man-in-the-middle attacks."
         ),
         tip="Understand port numbers too: HTTP is 80, HTTPS is 443.",
         tags="networking, HTTP, HTTPS, TLS, security"),

    dict(faculty="computer_science", difficulty="intermediate", order=7,
         question="What is a RESTful API and what are its key constraints?",
         answer=(
             "REST (Representational State Transfer) is an architectural style for "
             "designing networked APIs. Key constraints: "
             "1) Stateless – each request carries all needed information. "
             "2) Client-Server separation. "
             "3) Uniform Interface – standard HTTP methods (GET, POST, PUT, DELETE). "
             "4) Cacheable responses. "
             "5) Layered System. "
             "Resources are identified by URIs and representations are usually JSON or XML."
         ),
         tip="Know the difference between PUT (full replace) and PATCH (partial update).",
         tags="API, REST, HTTP methods, JSON, web services"),

    dict(faculty="computer_science", difficulty="intermediate", order=8,
         question="What is the difference between SQL and NoSQL databases?",
         answer=(
             "SQL databases (e.g., PostgreSQL, MySQL) store data in structured tables "
             "with a fixed schema and support ACID transactions. They excel at complex "
             "queries and relationships. NoSQL databases (e.g., MongoDB, Redis) store "
             "data in flexible formats (documents, key-value, graphs) and scale "
             "horizontally more easily. Choose SQL for structured, relational data; "
             "NoSQL for flexible schemas or very high write loads."
         ),
         tip="Mention a use-case for each to show practical understanding.",
         tags="SQL, NoSQL, databases, PostgreSQL, MongoDB"),

    dict(faculty="computer_science", difficulty="beginner", order=9,
         question="What is recursion? Give an example.",
         answer=(
             "Recursion is when a function calls itself to solve a smaller instance of "
             "the same problem. Every recursive function needs a base case to stop. "
             "Example: factorial(n) = n * factorial(n-1), with base case factorial(0) = 1. "
             "Other examples: tree traversal, merge sort, Fibonacci sequence."
         ),
         tip="Be able to trace through a recursive call stack on paper.",
         tags="recursion, algorithms, base case, factorial"),

    dict(faculty="computer_science", difficulty="intermediate", order=10,
         question="What is Big-O notation? What is the time complexity of binary search?",
         answer=(
             "Big-O notation describes the worst-case growth rate of an algorithm's "
             "time or space usage as input size n grows. Common complexities: "
             "O(1) constant, O(log n) logarithmic, O(n) linear, O(n log n) linearithmic, "
             "O(n²) quadratic. Binary search runs in O(log n) because each step halves "
             "the search space."
         ),
         tip="Practice analysing simple loops and nested loops.",
         tags="Big-O, complexity, binary search, algorithms"),

    dict(faculty="computer_science", difficulty="intermediate", order=11,
         question="What is the difference between a process and a thread?",
         answer=(
             "A process is an independent program in execution with its own memory space. "
             "A thread is a lighter unit of execution within a process that shares the "
             "process's memory. Threads are faster to create and communicate, but bugs "
             "like race conditions are harder to debug. Use threads for concurrent tasks "
             "within one program; use processes for isolation."
         ),
         tip="Know what a deadlock is and how to avoid it.",
         tags="OS, processes, threads, concurrency, deadlock"),

    dict(faculty="computer_science", difficulty="beginner", order=12,
         question="What development tools and IDEs have you used?",
         answer=(
             "Mention tools you genuinely use: VS Code, PyCharm, IntelliJ, Eclipse, etc. "
             "Also mention adjacent tools: Git for version control, Docker if applicable, "
             "Postman for API testing, browser DevTools for front-end work."
         ),
         tip="Be ready to demonstrate proficiency if asked.",
         tags="IDE, VS Code, tools, developer workflow"),

    dict(faculty="computer_science", difficulty="intermediate", order=13,
         question="Can you explain the MVC design pattern?",
         answer=(
             "MVC (Model-View-Controller) separates an application into three layers: "
             "Model – manages data and business logic; "
             "View – the user interface that displays data; "
             "Controller – handles user input and updates the model or view. "
             "This separation makes code easier to maintain and test. "
             "Django follows MVT (Model-View-Template), a close variant."
         ),
         tip="Give a concrete example from a project you have built.",
         tags="MVC, design patterns, architecture, Django"),

    dict(faculty="computer_science", difficulty="advanced", order=14,
         question="What is a hash table and how does it handle collisions?",
         answer=(
             "A hash table maps keys to values using a hash function that converts a key "
             "into an array index. Average-case lookup is O(1). Collisions (two keys "
             "mapping to the same index) are handled by: "
             "1) Chaining – each slot holds a linked list of entries; "
             "2) Open addressing – probe for the next empty slot (linear, quadratic probing, "
             "or double hashing)."
         ),
         tip="Know the load factor and when to resize a hash table.",
         tags="hash table, hashing, collisions, data structures"),

    dict(faculty="computer_science", difficulty="advanced", order=15,
         question="Explain the concept of normalisation in databases.",
         answer=(
             "Normalisation is the process of structuring a relational database to reduce "
             "redundancy and improve data integrity. Key normal forms: "
             "1NF – each column has atomic values, no repeating groups. "
             "2NF – in 1NF and every non-key attribute is fully dependent on the whole key. "
             "3NF – in 2NF and no transitive dependencies. "
             "BCNF is a stricter 3NF. Denormalisation is sometimes done for performance."
         ),
         tip="Be able to spot a violation and fix it with an example table.",
         tags="databases, normalisation, 1NF, 2NF, 3NF, SQL"),

    dict(faculty="computer_science", difficulty="intermediate", order=16,
         question="What is the difference between synchronous and asynchronous programming?",
         answer=(
             "Synchronous code executes line by line; each step waits for the previous "
             "to finish. Asynchronous code allows operations (e.g., network requests) to "
             "run in the background while other code continues. In JavaScript, this is "
             "handled with callbacks, Promises, and async/await. In Python, asyncio "
             "provides similar capabilities."
         ),
         tip="Know why async is important for I/O-bound tasks like API calls.",
         tags="async, sync, JavaScript, Python, promises, await"),

    dict(faculty="computer_science", difficulty="beginner", order=17,
         question="What is the difference between front-end and back-end development?",
         answer=(
             "Front-end (client-side) development concerns everything the user sees and "
             "interacts with in the browser—HTML, CSS, JavaScript, and frameworks like "
             "React or Vue. Back-end (server-side) handles data storage, business logic, "
             "and APIs—using languages like Python, Node.js, Java, PHP and databases. "
             "Full-stack developers work on both."
         ),
         tip="Know which end you are stronger in and be honest.",
         tags="front-end, back-end, full-stack, web development"),

    dict(faculty="computer_science", difficulty="intermediate", order=18,
         question="What is a primary key and a foreign key in a relational database?",
         answer=(
             "A primary key uniquely identifies each row in a table—it must be unique "
             "and not null. A foreign key is a column in one table that references the "
             "primary key in another table, establishing a relationship. Foreign keys "
             "enforce referential integrity: you cannot have a foreign key value that "
             "does not exist in the referenced table."
         ),
         tip="Draw a simple schema to illustrate when explaining.",
         tags="database, primary key, foreign key, relational, SQL"),

    dict(faculty="computer_science", difficulty="beginner", order=19,
         question="Have you worked on any personal or academic projects? Describe one.",
         answer=(
             "Choose a project you are genuinely proud of. Describe the problem it solved, "
             "the technology stack you used, your role, a challenge you overcame, and the "
             "outcome. If it is on GitHub, mention it."
         ),
         tip="Concrete projects are your most powerful selling point as a student. "
             "Even a small finished project beats a dozen unfinished ones.",
         tags="projects, portfolio, GitHub, practical experience"),

    dict(faculty="computer_science", difficulty="intermediate", order=20,
         question="What is the difference between compiled and interpreted languages?",
         answer=(
             "Compiled languages (C, C++, Go) translate source code to machine code "
             "before execution, producing a standalone executable—generally faster at "
             "runtime. Interpreted languages (Python, JavaScript, Ruby) are translated "
             "line-by-line at runtime by an interpreter—easier to develop and debug but "
             "typically slower. Java uses a hybrid: compiled to bytecode, then run by the JVM."
         ),
         tip="Be able to explain where Python and Java fit on this spectrum.",
         tags="compiled, interpreted, Python, C, Java, runtime"),

    # ─── ENGINEERING ────────────────────────────────────────────────────────

    dict(faculty="engineering", difficulty="beginner", order=1,
         question="Explain the difference between AC and DC current.",
         answer=(
             "Direct Current (DC) flows in one direction continuously—used in batteries "
             "and electronics. Alternating Current (AC) periodically reverses direction—"
             "used in mains power supply because it is easier to transform to different "
             "voltages over long distances."
         ),
         tip="Know the standard mains voltage and frequency in Zimbabwe (240V, 50Hz).",
         tags="electrical, AC, DC, power"),

    dict(faculty="engineering", difficulty="beginner", order=2,
         question="What is AutoCAD and have you used it?",
         answer=(
             "AutoCAD is a computer-aided design (CAD) software for 2D and 3D drawings. "
             "Engineers use it to create technical drawings, blueprints, and models. "
             "Mention any experience with AutoCAD, SolidWorks, or other CAD tools from "
             "coursework or projects."
         ),
         tip="Even basic exposure shows initiative. Mention a specific drawing you made.",
         tags="AutoCAD, CAD, engineering drawings, design"),

    dict(faculty="engineering", difficulty="intermediate", order=3,
         question="What is a P&ID diagram?",
         answer=(
             "A Piping and Instrumentation Diagram (P&ID) is a detailed schematic showing "
             "pipes, vessels, instruments, valves, and control systems in a process plant. "
             "It uses standardised symbols and is essential for design, construction, and "
             "maintenance of process facilities."
         ),
         tip="Common in chemical and civil engineering attachments.",
         tags="P&ID, process engineering, chemical engineering, instrumentation"),

    dict(faculty="engineering", difficulty="beginner", order=4,
         question="What health and safety practices are important on a construction or plant site?",
         answer=(
             "Always wear appropriate PPE (hard hat, safety boots, gloves, goggles). "
             "Follow lockout/tagout procedures. Attend site inductions. Never bypass "
             "safety interlocks. Report near-misses. Know emergency exits and first aid "
             "locations. In Zimbabwe, the Zimbabwe Occupational Safety Council (ZISCO) "
             "standards apply."
         ),
         tip="Emphasise a safety-first mindset—supervisors value students who ask "
             "before touching unfamiliar equipment.",
         tags="health and safety, PPE, OSHA, construction, Zimbabwe"),

    # ─── BUSINESS ───────────────────────────────────────────────────────────

    dict(faculty="business", difficulty="beginner", order=1,
         question="What is a SWOT analysis?",
         answer=(
             "SWOT stands for Strengths, Weaknesses, Opportunities, Threats. It is a "
             "strategic planning tool used to evaluate internal factors (strengths and "
             "weaknesses) and external factors (opportunities and threats) affecting an "
             "organisation or project."
         ),
         tip="Be ready to do a SWOT on the company you are interviewing at.",
         tags="SWOT, strategy, business analysis"),

    dict(faculty="business", difficulty="beginner", order=2,
         question="What accounting software are you familiar with?",
         answer=(
             "Mention packages from your coursework or personal use: Pastel, Sage, "
             "QuickBooks, Xero, or even Excel-based accounting. Highlight any modules "
             "on accounting information systems."
         ),
         tip="Most Zimbabwean SMEs use Pastel or Sage—knowing these is an advantage.",
         tags="accounting software, Pastel, Sage, QuickBooks, finance"),

    dict(faculty="business", difficulty="intermediate", order=3,
         question="Explain the difference between gross profit and net profit.",
         answer=(
             "Gross profit = Revenue – Cost of Goods Sold (COGS). It measures how "
             "efficiently a company produces its goods. Net profit = Gross profit – "
             "Operating expenses – Interest – Taxes. It is the final profit after all "
             "costs and is the 'bottom line'."
         ),
         tip="Know the income statement structure; interviewers in finance love this.",
         tags="accounting, profit, income statement, finance, gross, net"),

    # ─── SOCIAL & BEHAVIOURAL SCIENCE ───────────────────────────────────────

    dict(faculty="social_behavioural", difficulty="beginner", order=1,
         question="What is the difference between qualitative and quantitative research?",
         answer=(
             "Quantitative research deals with numerical data and statistical analysis to "
             "find patterns or test hypotheses—e.g., surveys with Likert scales. "
             "Qualitative research explores meaning, experiences, and perspectives through "
             "non-numerical data—e.g., interviews, focus groups, observation. Mixed-methods "
             "research combines both."
         ),
         tip="Know which method suits which type of research question.",
         tags="research methods, qualitative, quantitative, mixed methods"),

    dict(faculty="social_behavioural", difficulty="intermediate", order=2,
         question="What is informed consent in social research?",
         answer=(
             "Informed consent means participants voluntarily agree to take part after "
             "being fully informed about the study's purpose, procedures, risks, and their "
             "right to withdraw at any time without penalty. It is a core ethical "
             "requirement from bodies like the Research Council of Zimbabwe."
         ),
         tip="Be prepared to discuss how you would obtain consent in a field study.",
         tags="ethics, research, informed consent, social science"),

    # ─── MEDICINE & HEALTH SCIENCES ─────────────────────────────────────────

    dict(faculty="medicine", difficulty="beginner", order=1,
         question="Why did you choose medicine/healthcare?",
         answer="I want to make a tangible difference in people's lives and I am fascinated by human biology and the application of science to heal.",
         tip="Show genuine empathy and passion for the field, rather than just stating it's a stable career.",
         tags="motivation, healthcare, empathy"),

    dict(faculty="medicine", difficulty="intermediate", order=2,
         question="How do you handle high-stress situations or medical emergencies?",
         answer="I remain calm, follow standard protocols (like ABCDE in trauma), prioritise tasks, and communicate clearly with the team. Seeking senior help when necessary is also crucial.",
         tip="Interviewers want to know you are safe and know your limits.",
         tags="stress management, emergencies, safety"),

    # ─── LAW ────────────────────────────────────────────────────────────────

    dict(faculty="law", difficulty="beginner", order=1,
         question="Why do you want to pursue a career in law?",
         answer="I have a strong sense of justice, enjoy analytical problem-solving, and want to advocate for those who cannot easily navigate the legal system.",
         tip="Connect your answer to the specific area of law the firm practices.",
         tags="motivation, law, justice"),

    dict(faculty="law", difficulty="intermediate", order=2,
         question="How do you approach a complex legal research task?",
         answer="I start by identifying the key legal issues, use primary sources like statutes and case law, and then consult secondary sources like journals. I ensure all findings are meticulously documented.",
         tip="Mention specific research tools like LexisNexis or Westlaw if you have used them.",
         tags="research, problem-solving, analysis"),

    # ─── ARTS & HUMANITIES ──────────────────────────────────────────────────

    dict(faculty="arts", difficulty="beginner", order=1,
         question="How do the arts/humanities contribute to society?",
         answer="They foster critical thinking, empathy, and cultural understanding. They help us analyse history, communicate complex ideas, and solve problems creatively.",
         tip="Be prepared to give an example from your own studies.",
         tags="value of arts, critical thinking, society"),

    # ─── NATURAL SCIENCES ───────────────────────────────────────────────────

    dict(faculty="natural_sciences", difficulty="intermediate", order=1,
         question="Describe a laboratory experiment you designed or conducted.",
         answer="I formulated a clear hypothesis, designed a controlled experiment, carefully collected and recorded data, and analysed the results to draw a conclusion, while strictly adhering to lab safety protocols.",
         tip="Focus on your methodology and problem-solving skills during the experiment.",
         tags="lab skills, scientific method, experiment"),

    # ─── EDUCATION ──────────────────────────────────────────────────────────

    dict(faculty="education", difficulty="beginner", order=1,
         question="What is your teaching philosophy?",
         answer="I believe in student-centered learning where the teacher acts as a facilitator. I aim to create an inclusive environment that caters to different learning styles.",
         tip="Keep it concise and focus on the student's experience.",
         tags="teaching philosophy, education, pedagogy"),

    # ─── RESEARCHED INTERNSHIP / ATTACHMENT BANK ───────────────────────────
    # Built from university career-center guidance, NACE competencies, and
    # technical interview guidance from Harvard, UMD, UMBC, UIC, Michigan,
    # Texas CNS, Tufts, and Colorado Boulder.

    dict(faculty="general", difficulty="beginner", order=101,
         question="Why are you interested in this internship or attachment placement?",
         answer=(
             "Connect the placement to your degree, skills you want to build, and the "
             "organization's work. Mention one or two specific things you researched, "
             "then explain how you can contribute as a student while learning from the team."
         ),
         tip="Avoid a generic answer. Show that you understand the organization and the role.",
         tags="internship, attachment, motivation, company research"),

    dict(faculty="general", difficulty="intermediate", order=102,
         question="Tell me about a time you had to learn something quickly.",
         answer=(
             "Use STAR: explain the situation, what you needed to learn, how you found "
             "resources or mentors, and the result. End with how that habit will help you "
             "settle into an internship team."
         ),
         tip="Employers use this to assess curiosity, adaptability, and self-development.",
         tags="behavioral, STAR, learning, adaptability"),

    dict(faculty="general", difficulty="intermediate", order=103,
         question="Describe a time you worked with a difficult teammate.",
         answer=(
             "Focus on communication and responsibility. Explain how you listened, clarified "
             "expectations, documented tasks, and kept the project moving without attacking "
             "the person."
         ),
         tip="Do not blame the teammate. Show maturity, teamwork, and conflict management.",
         tags="behavioral, teamwork, conflict, professionalism"),

    dict(faculty="general", difficulty="beginner", order=104,
         question="Which course or project best prepared you for this role?",
         answer=(
             "Choose a relevant course or project, briefly describe the problem, tools used, "
             "your specific contribution, and the result. Link the project to the internship's "
             "daily work."
         ),
         tip="Specific examples are stronger than listing every course on your transcript.",
         tags="academic, projects, internship, preparation"),

    dict(faculty="general", difficulty="intermediate", order=105,
         question="Tell me about a time you received critical feedback.",
         answer=(
             "Describe the feedback, how you responded professionally, what you changed, "
             "and what improved. A lecturer's comment, code review, supervisor note, or "
             "peer critique can all work."
         ),
         tip="This question tests growth mindset and professionalism.",
         tags="behavioral, feedback, growth mindset, professionalism"),

    dict(faculty="computer_science", difficulty="beginner", order=101,
         question="How would you troubleshoot a computer that cannot connect to the internet?",
         answer=(
             "Check whether the issue affects one device or many, confirm Wi-Fi/Ethernet "
             "connection, test another site, inspect IP/DNS settings, restart the adapter or "
             "router, and escalate with clear notes if the problem persists."
         ),
         tip="For IT support roles, interviewers value a calm, step-by-step process.",
         tags="information technology, troubleshooting, networking, support"),

    dict(faculty="computer_science", difficulty="beginner", order=102,
         question="Explain DNS in simple terms.",
         answer=(
             "DNS is the internet's naming system. It translates human-readable domain names "
             "like example.com into IP addresses that computers use to find servers."
         ),
         tip="Use an analogy, then mention one practical debugging tool such as nslookup or dig.",
         tags="information technology, DNS, networking"),

    dict(faculty="computer_science", difficulty="intermediate", order=103,
         question="What is the difference between authentication and authorization?",
         answer=(
             "Authentication verifies who a user is, such as logging in with a password or "
             "multi-factor code. Authorization decides what that verified user is allowed to "
             "access, such as admin-only pages or specific records."
         ),
         tip="Give a real application example to make the distinction clear.",
         tags="security, authentication, authorization, web development"),

    dict(faculty="computer_science", difficulty="intermediate", order=104,
         question="How do you test a feature before handing it over?",
         answer=(
             "Check the happy path, validation errors, edge cases, and any regression risk. "
             "Use automated tests where possible, then do a short manual smoke test that "
             "matches how users will actually use the feature."
         ),
         tip="This is practical software engineering, not just theory.",
         tags="software engineering, testing, QA, debugging"),

    dict(faculty="computer_science", difficulty="advanced", order=105,
         question="How would you design a small REST API for interview questions?",
         answer=(
             "Model the resource, expose clear endpoints such as GET /questions/ and "
             "POST /questions/submit/, validate inputs, paginate lists, return proper HTTP "
             "status codes, and keep pending submissions separate from public approved data."
         ),
         tip="Mention status codes, validation, pagination, and access control.",
         tags="REST, API design, Django, backend"),

    dict(faculty="business", difficulty="beginner", order=101,
         question="How would you analyse why monthly sales dropped?",
         answer=(
             "Compare sales by product, branch, customer segment, and time period. Check "
             "price changes, stock availability, marketing activity, seasonality, competitor "
             "moves, and customer feedback before recommending action."
         ),
         tip="Show structured thinking before jumping to a conclusion.",
         tags="business analysis, sales, commerce, problem solving"),

    dict(faculty="business", difficulty="intermediate", order=102,
         question="What financial statements would you review to understand a company?",
         answer=(
             "Review the income statement for profitability, balance sheet for assets, "
             "liabilities and equity, and cash-flow statement for liquidity. Together they "
             "show performance, financial position, and cash health."
         ),
         tip="Keep it practical; explain what each statement helps you decide.",
         tags="finance, accounting, financial statements"),

    dict(faculty="business", difficulty="beginner", order=103,
         question="How would you handle an unhappy customer?",
         answer=(
             "Listen without interrupting, acknowledge the problem, ask clarifying questions, "
             "offer a realistic solution within policy, and follow up to make sure the issue "
             "was resolved."
         ),
         tip="Customer-facing interns are judged on patience and communication.",
         tags="customer service, communication, professionalism"),

    dict(faculty="business", difficulty="intermediate", order=104,
         question="How would you measure whether a marketing campaign worked?",
         answer=(
             "Define the goal first, such as leads, sales, reach, engagement, or retention. "
             "Then compare metrics before and after the campaign, track conversion rates, "
             "and consider cost per result."
         ),
         tip="Tie metrics to business objectives, not vanity numbers only.",
         tags="marketing, analytics, campaign measurement"),

    dict(faculty="engineering", difficulty="beginner", order=101,
         question="Tell me about a technical project where your first design did not work.",
         answer=(
             "Explain the design goal, what failed, how you diagnosed the issue, what you "
             "changed, and what you learned. Emphasize safety, testing, and documentation."
         ),
         tip="Engineering interviewers value how you think through failure.",
         tags="engineering, design, failure, problem solving"),

    dict(faculty="engineering", difficulty="intermediate", order=102,
         question="How do you approach safety before starting practical or site work?",
         answer=(
             "Identify hazards, understand procedures, use required PPE, confirm tools and "
             "materials are suitable, ask questions when unclear, and stop work if conditions "
             "are unsafe."
         ),
         tip="Safety awareness is essential even for junior attachment students.",
         tags="engineering, safety, site work, professionalism"),

    dict(faculty="engineering", difficulty="intermediate", order=103,
         question="How would you explain a technical issue to a non-technical manager?",
         answer=(
             "Start with the impact on cost, time, safety, or quality. Use plain language, "
             "avoid unnecessary formulas, provide options, and recommend the next action."
         ),
         tip="Good engineers translate complexity into decisions.",
         tags="engineering, communication, technical explanation"),

    dict(faculty="social_behavioural", difficulty="beginner", order=101,
         question="How would you handle confidential information during fieldwork?",
         answer=(
             "Collect only what is needed, get informed consent where required, anonymize "
             "responses, store records securely, and discuss data only with authorized people."
         ),
         tip="Ethics and confidentiality matter in social-science placements.",
         tags="social sciences, ethics, confidentiality, fieldwork"),

    dict(faculty="social_behavioural", difficulty="intermediate", order=102,
         question="Describe how you would build trust with community participants.",
         answer=(
             "Be respectful, explain the purpose clearly, listen before advising, keep "
             "promises, use appropriate language, and work through accepted community channels."
         ),
         tip="Show cultural awareness and humility.",
         tags="social sciences, community work, communication, empathy"),

    dict(faculty="social_behavioural", difficulty="intermediate", order=103,
         question="What would you do if survey responses seemed biased?",
         answer=(
             "Review the sample, wording, data collection method, and interviewer influence. "
             "Report limitations honestly and, if possible, triangulate with other data sources."
         ),
         tip="Do not hide limitations. Good researchers disclose them.",
         tags="research methods, surveys, bias, analysis"),

    dict(faculty="medicine", difficulty="beginner", order=101,
         question="Why are empathy and professionalism important in health placements?",
         answer=(
             "Patients and colleagues need to feel respected and safe. Empathy helps you "
             "understand patient concerns, while professionalism protects confidentiality, "
             "team trust, and quality of care."
         ),
         tip="Health interviews often assess maturity beyond grades.",
         tags="health sciences, empathy, professionalism, patient care"),

    dict(faculty="medicine", difficulty="intermediate", order=102,
         question="How would you respond if you made a mistake during a clinical or lab task?",
         answer=(
             "Stop, make the situation safe, inform the supervisor immediately, document "
             "truthfully according to procedure, and reflect on how to prevent recurrence."
         ),
         tip="Honesty and safety are more important than pretending nothing happened.",
         tags="health sciences, safety, integrity, clinical placement"),

    dict(faculty="medicine", difficulty="intermediate", order=103,
         question="How do you manage stress in a high-pressure health environment?",
         answer=(
             "Prioritize urgent tasks, communicate early, follow protocols, take brief resets "
             "when possible, and seek supervision rather than making unsafe decisions alone."
         ),
         tip="Balance resilience with knowing when to ask for help.",
         tags="health sciences, stress management, teamwork"),

    dict(faculty="natural_sciences", difficulty="intermediate", order=101,
         question="How do you ensure accuracy when recording lab data?",
         answer=(
             "Use standard procedures, label samples clearly, record observations immediately, "
             "check units, keep raw data unchanged, and ask for verification when results look unusual."
         ),
         tip="Accuracy and traceability are central to scientific work.",
         tags="laboratory, data accuracy, scientific method"),

    dict(faculty="education", difficulty="beginner", order=101,
         question="How would you support learners with different ability levels?",
         answer=(
             "Plan varied activities, check understanding frequently, give extra support where "
             "needed, challenge stronger learners appropriately, and keep the classroom respectful."
         ),
         tip="Show inclusive, student-centered thinking.",
         tags="education, inclusion, classroom support"),

]


class Command(BaseCommand):
    help = "Seed the database with approved interview questions and CV builders."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all existing InterviewQuestion and CVBuilder records before seeding.",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            deleted_questions, _ = InterviewQuestion.objects.all().delete()
            deleted_builders, _ = CVBuilder.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(
                    f"Deleted {deleted_questions} existing questions and {deleted_builders} existing CV builders."
                )
            )

        created = 0
        updated = 0

        for q in QUESTIONS:
            defaults = q.copy()
            defaults["status"] = "approved"
            defaults.setdefault("submitted_by_name", "")
            defaults.setdefault("submitted_by_email", "")
            obj, was_created = InterviewQuestion.objects.update_or_create(
                question=q["question"],
                defaults=defaults,
            )
            if was_created:
                created += 1
            else:
                updated += 1

        builder_created = 0
        builder_updated = 0
        for builder in CV_BUILDERS:
            defaults = builder.copy()
            defaults["status"] = "approved"
            defaults.setdefault("submitted_by_name", "")
            defaults.setdefault("submitted_by_email", "")
            obj, was_created = CVBuilder.objects.update_or_create(
                link=builder["link"],
                defaults=defaults,
            )
            if was_created:
                builder_created += 1
            else:
                builder_updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Seeding complete. "
                f"Questions created: {created} | Questions updated: {updated} | "
                f"CV builders created: {builder_created} | CV builders updated: {builder_updated}"
            )
        )
