# **Take Home: Build a Job Ingestion and Search System**

You are tasked with designing a system that first ingesting job postings from various sources and determining whether each job should be approved for publication on The Ladders' platform. then allows users to search, filter, and sort approved jobs.

---

### **Overview**

- **Ingestion Process:** The system should parse job postings in various JSON formats and transform them into a common internal representation.
- **Approval Process:** After ingestion, each job posting should be evaluated against specific criteria to decide whether it should be approved or rejected.
- **Storage:** Approved job postings will be stored for publication, while rejected ones should be logged for review.
- **UX**: Provide a simple UI for users to search, filter, and sort approved jobs

### **Requirements**

1. **Data Modeling**
  - Create data structures to represent job postings, ensuring all essential fields are included.
  - Use appropriate data types and structures to represent fields such as employment type, location, salary, etc.
2. **Ingestion**
  - Implement a component that reads job postings from a JSON files and converts them into the internal representation.
  - Ensure the ingestion process can handle multiple job postings and is robust against invalid data.
3. **Approval Criteria**
  - **Title** must not be null or empty
  - **Geographical Location:** Job must be either remote (anywhere) or in-person located within the United States or Canada.
  - **Employment Type:** Job must be a full-time position.
  - **Salary Requirement:** Annual salary must be over $100,000 (US Dollars) or above $45/hour (when billed per hour).
  - **Company Type:** Job must not be from a staffing firm.
  - **Language Requirement:** Job description must be in English (or French if the job is in Canada).
4. **Approval Process**
  - Implement a component that applies the approval criteria to each job posting.
  - Jobs that meet all criteria should be marked as approved; others should be marked as rejected with reasons.
5. **Storage and Logging**
  - Approved jobs should be stored in a way that they can be retrieved for search (e.g., in-memory list, mocked database, or local file).
  - Rejected jobs should be logged along with the reasons for rejection.
6. **UX**
  - User should be able to see all the jobs in a list
  - User can search jobs by title
  - User can filter jobs by country
  - User can sort jobs by salary and posting date
7. **Code Organization**
  - Organize your code into logical modules or packages (e.g., `models`, `ingestion`, `approval`, `storage`).
  - Use clear and descriptive naming conventions for variables, functions, classes, and modules.

---

## **Test Data**

```json
[
  {
    "title": "Backend Engineer",
    "description": "Join our backend team to build scalable APIs using Go and microservices architecture.",
    "company": "NextGen Systems",
    "location": { "city": "Austin", "state": "TX", "country": "USA" },
    "salary": { "value": 145000, "currency": "USD" },
    "employment_type": "Full-Time",
    "posting_date": "2023-10-03",
    "company_type": "Direct Employer",
    "language": "English",
    "remote": false
  },
  {
    "title": "Frontend Developer Intern",
    "description": "Looking for an enthusiastic intern to assist in frontend development with React.",
    "company": "BrightStart Talent",
    "location": { "city": "Vancouver", "state": "BC", "country": "Canada" },
    "salary": { "value": 20000, "currency": "CAD" },
    "employment_type": "Internship",
    "posting_date": "2023-10-06",
    "company_type": "Staffing Firm",
    "language": "English",
    "remote": false
  },
  {
    "title": "Machine Learning Engineer",
    "description": "Rejoignez notre équipe pour développer des modèles de machine learning avancés.",
    "company": "DeepData Labs",
    "location": { "city": "Montreal", "state": "QC", "country": "Canada" },
    "salary": { "value": 120000, "currency": "USD" },
    "employment_type": "Full-Time",
    "posting_date": "2023-10-11",
    "company_type": "Direct Employer",
    "language": "French",
    "remote": false
  },
  {
    "title": "Agile Project Lead",
    "description": "Drive cross-functional teams in a remote-first environment with agile principles.",
    "company": "Orbit Global",
    "location": { "city": "Manchester", "state": "England", "country": "UK" },
    "salary": { "value": 85000, "currency": "GBP" },
    "employment_type": "Full-Time",
    "posting_date": "2023-10-13",
    "company_type": "Direct Employer",
    "language": "English",
    "remote": true
  },
  {
    "title": "DevOps Consultant",
    "description": "We are seeking a highly skilled DevOps Consultant.",
    "company": "CloudWorks Pro",
    "location": { "city": "Seattle", "state": "WA", "country": "USA" },
    "salary": { "value": 65, "currency": "USD", "unit": "hourly" },
    "employment_type": "Contract",
    "posting_date": "2023-10-14",
    "company_type": "Consulting Agency",
    "language": "English",
    "remote": true
  },
  {
    "title": "Senior Software Engineer",
    "description": "We are looking for a Senior Software Engineer.",
    "company": "Tech Innovators Inc.",
    "location": "New York, NY, USA",
    "salary": 150000,
    "employment_type": "Full-Time",
    "posting_date": "2023-10-01",
    "company_type": "Direct Employer",
    "language": "English",
    "remote": false
  },
  {
    "title": "Junior Developer",
    "description": "An excellent opportunity for a Junior Developer.",
    "company": "Staffing Solutions",
    "location": "Toronto, ON, Canada",
    "salary": 80000,
    "employment_type": "Full-Time",
    "posting_date": "2023-10-05",
    "company_type": "Staffing Firm",
    "language": "",
    "remote": false
  },
  {
    "title": "Data Scientist",
    "description": "Nous recherchons un Data Scientist expérimenté.",
    "company": "Analytics Corp.",
    "location": "Montreal, QC, Canada",
    "salary": 62.5,
    "employment_type": "Full-Time",
    "posting_date": "2023-10-10",
    "company_type": "Direct Employer",
    "language": "French",
    "remote": false
  },
  {
    "title": "Project Manager",
    "description": "Lead projects across various domains.",
    "company": "Global Enterprises",
    "location": "London, UK",
    "salary": 80000,
    "employment_type": "Full-Time",
    "posting_date": "2023-10-12",
    "company_type": "Direct Employer",
    "language": "English",
    "remote": true
  },
  {
    "title": "QA Automation Engineer",
    "description": "Build automated test suites.",
    "company": "QualityLoop",
    "location": { "city": "Chicago", "state": "IL", "country": "USA" },
    "salary": { "value": 110000, "currency": "USD" },
    "employment_type": "Full-Time",
    "posting_date": "2023-10-15",
    "company_type": "Direct Employer",
    "language": "English",
    "remote": true
  },
  {
    "title": "UX Designer",
    "description": "Design intuitive user experiences.",
    "company": "PixelCraft Studio",
    "location": { "city": "", "state": "CA", "country": "USA" },
    "salary": { "value": 105000, "currency": "USD" },
    "employment_type": "Full-Time",
    "posting_date": "2023-10-16",
    "company_type": "Direct Employer",
    "language": "English",
    "remote": false
  },
  {
    "title": "Product Analyst",
    "description": "Analyze product usage data.",
    "company": "MetricMind",
    "location": "Boston, MA, USA",
    "salary": 120000,
    "employment_type": "Full-Time",
    "posting_date": "2023-10-17",
    "company_type": "Direct Employer",
    "language": "English",
    "remote": false
  },
  {
    "title": "Mobile Engineer",
    "description": "Develop mobile applications.",
    "company": "AppForge",
    "location": { "city": "Berlin", "state": "", "country": "Germany" },
    "salary": { "value": 78000, "currency": "EUR" },
    "employment_type": "Full-Time",
    "posting_date": "2023-10-18",
    "company_type": "Direct Employer",
    "language": "German",
    "remote": false
  },
  {
    "title": "Technical Writer",
    "description": "Create developer documentation.",
    "company": "DocuFlow",
    "location": "Remote",
    "salary": 90000,
    "employment_type": "Part-Time",
    "posting_date": "2023-10-19",
    "company_type": "Consulting Agency",
    "language": "English",
    "remote": true
  },
  {
    "title": "Cybersecurity Specialist",
    "description": "Monitor security events.",
    "company": "SecurePath",
    "location": { "city": "Washington", "state": "DC", "country": "USA" },
    "salary": { "value": 135000, "currency": "USD" },
    "employment_type": "Full-Time",
    "posting_date": "2023-10-20",
    "company_type": "Direct Employer",
    "language": "English",
    "remote": false
  },
  {
    "title": "Growth Marketing Manager",
    "description": "Own acquisition campaigns.",
    "company": "ScaleRocket",
    "location": "San Francisco, CA, USA",
    "salary": 125000,
    "employment_type": "Full-Time",
    "posting_date": "",
    "company_type": "Direct Employer",
    "language": "English",
    "remote": true
  },
  {
    "title": "Database Administrator",
    "description": "Maintain databases.",
    "company": "DataCore Services",
    "location": { "city": "Dublin", "state": "Leinster", "country": "Ireland" },
    "salary": { "value": 58, "currency": "EUR", "unit": "hourly" },
    "employment_type": "Contract",
    "posting_date": "2023-10-21",
    "company_type": "Staffing Firm",
    "language": "English",
    "remote": true
  },
  {
    "title": "Business Operations Associate",
    "description": "Support operations.",
    "company": "Northstar Group",
    "location": "Atlanta, GA, USA",
    "salary": 72000,
    "employment_type": "Full-Time",
    "posting_date": "2023-10-22",
    "company_type": "Direct Employer",
    "language": "English",
    "remote": false
  },
  {
    "title": "Customer Success Manager",
    "description": "Help customers onboard.",
    "company": "ClientBridge",
    "location": { "city": "Toronto", "state": "ON", "country": "Canada" },
    "salary": { "value": 110000, "currency": "USD" },
    "employment_type": "Full-Time",
    "posting_date": "2023-10-23",
    "company_type": "Direct Employer",
    "language": "English",
    "remote": false
  },
  {
    "title": "",
    "description": "Temporary support role.",
    "company": "OpsFlex",
    "location": null,
    "salary": { "value": 40, "currency": "USD", "unit": "hourly" },
    "employment_type": "Contract",
    "posting_date": "2023-10-24",
    "company_type": "Staffing Firm",
    "language": "English",
    "remote": true
  }
]

```

---

### **Instructions**

- **Design and implement** the system according to the requirements outlined above.
- **Data Integrity:** Ensure that your data models are robust and prevent invalid states. When making assumptions about the data, **keep in mind that it could be a data scraped as-is directly from the job posting page by 3rd party.** Some data might be missing and it has to be handled gracefully.
- Focus on **creating a clean and maintainable architecture** that separates concerns appropriately. **Think about how the process should be split into components, how should the processing pipeline be set up.**
- **Attached data contains corner cases.** Take a close look at the provided salary values, locations, etc - it simulates data scraped from website by 3rd party - dubious quality is expected. **Do not focus on location parsing, though -** any simple split by `,` and country name match will suffice.
- **Design the system so it’s flexible** - in future we might need to add additional conditions (for example, remote UK job could be approved with 90k USD compensation or more).
- **Design with tests in mind** - set up the system so it can be conveniently tested.
- You may mock implementations and external dependencies like databases or external services; **structure and design should be production ready, though.**
- **Make sure your code works and both feeds do parse correctly;** Review the results, make sure everything works as you expect.
- **Make sure you catch different use cases on the job search experience**
- Ideally use **Go, Typed Python (3.10+)** at the backend and **React/Typescript** at the Frontend**.**
- Use any IDE you’re most comfortable with.
- Usage of AI agents **is acceptable but you are expected to display full ownership of the solution.**

