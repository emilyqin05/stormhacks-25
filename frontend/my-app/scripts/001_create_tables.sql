-- Create jobs table
CREATE TABLE IF NOT EXISTS jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  department TEXT NOT NULL,
  location TEXT NOT NULL,
  type TEXT NOT NULL, -- Full-time, Part-time, Contract
  salary_range TEXT,
  description TEXT NOT NULL,
  requirements TEXT[] NOT NULL,
  responsibilities TEXT[] NOT NULL,
  posted_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  status TEXT DEFAULT 'active' -- active, closed
);

-- Create applicants table
CREATE TABLE IF NOT EXISTS applicants (
  applicant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  resume_url TEXT NOT NULL,
  applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE applicants ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Anyone can view active jobs"
  ON jobs FOR SELECT
  USING (status = 'active');

CREATE POLICY "Anyone can submit applications"
  ON applicants FOR INSERT
  WITH CHECK (true);

-- Insert mock job postings
INSERT INTO jobs (id, title, department, location, type, salary_range, description, requirements, responsibilities) VALUES
(
  '550e8400-e29b-41d4-a716-446655440001',
  'Senior Frontend Engineer',
  'Engineering',
  'San Francisco, CA (Hybrid)',
  'Full-time',
  '$140,000 - $180,000',
  'We''re looking for an experienced Frontend Engineer to join our growing team. You''ll work on building beautiful, performant user interfaces that delight our customers and push the boundaries of web technology.',
  ARRAY[
    '5+ years of experience with React and modern JavaScript',
    'Strong understanding of web performance optimization',
    'Experience with TypeScript and Next.js',
    'Excellent communication and collaboration skills',
    'Portfolio demonstrating exceptional UI/UX work'
  ],
  ARRAY[
    'Build and maintain critical user-facing features',
    'Collaborate with designers to implement pixel-perfect interfaces',
    'Optimize applications for maximum speed and scalability',
    'Mentor junior engineers and contribute to technical decisions',
    'Participate in code reviews and maintain high code quality standards'
  ]
),
(
  '550e8400-e29b-41d4-a716-446655440002',
  'Product Designer',
  'Design',
  'Remote (US)',
  'Full-time',
  '$120,000 - $160,000',
  'Join our design team to create intuitive, beautiful experiences that solve real user problems. You''ll own the design process from research to final implementation, working closely with engineering and product teams.',
  ARRAY[
    '4+ years of product design experience',
    'Strong portfolio showcasing end-to-end design projects',
    'Proficiency in Figma and modern design tools',
    'Experience with design systems and component libraries',
    'Understanding of frontend development principles'
  ],
  ARRAY[
    'Lead design projects from concept to launch',
    'Conduct user research and usability testing',
    'Create wireframes, prototypes, and high-fidelity designs',
    'Collaborate with engineers to ensure design quality',
    'Contribute to and maintain our design system'
  ]
),
(
  '550e8400-e29b-41d4-a716-446655440003',
  'Backend Engineer',
  'Engineering',
  'New York, NY (On-site)',
  'Full-time',
  '$130,000 - $170,000',
  'We need a talented Backend Engineer to help us scale our infrastructure and build robust APIs. You''ll work on challenging problems involving distributed systems, databases, and high-traffic applications.',
  ARRAY[
    '3+ years of backend development experience',
    'Strong knowledge of Node.js, Python, or Go',
    'Experience with PostgreSQL and database optimization',
    'Understanding of microservices architecture',
    'Familiarity with cloud platforms (AWS, GCP, or Azure)'
  ],
  ARRAY[
    'Design and implement scalable backend services',
    'Build and maintain RESTful and GraphQL APIs',
    'Optimize database queries and system performance',
    'Implement security best practices and data protection',
    'Work with DevOps on deployment and monitoring'
  ]
),
(
  '550e8400-e29b-41d4-a716-446655440004',
  'Marketing Manager',
  'Marketing',
  'Austin, TX (Hybrid)',
  'Full-time',
  '$90,000 - $120,000',
  'Lead our marketing efforts to drive growth and brand awareness. You''ll develop and execute marketing strategies across multiple channels, working with a talented team to reach our target audience.',
  ARRAY[
    '5+ years of marketing experience, preferably in tech',
    'Proven track record of successful campaigns',
    'Strong analytical skills and data-driven mindset',
    'Experience with marketing automation tools',
    'Excellent written and verbal communication'
  ],
  ARRAY[
    'Develop and execute comprehensive marketing strategies',
    'Manage content creation and social media presence',
    'Analyze campaign performance and optimize for ROI',
    'Collaborate with sales team on lead generation',
    'Manage marketing budget and vendor relationships'
  ]
),
(
  '550e8400-e29b-41d4-a716-446655440005',
  'DevOps Engineer',
  'Engineering',
  'Remote (Global)',
  'Full-time',
  '$120,000 - $160,000',
  'Help us build and maintain world-class infrastructure. You''ll work on automation, monitoring, and ensuring our systems are reliable, secure, and scalable.',
  ARRAY[
    '3+ years of DevOps or SRE experience',
    'Strong knowledge of Docker, Kubernetes, and CI/CD',
    'Experience with infrastructure as code (Terraform, CloudFormation)',
    'Proficiency in scripting languages (Bash, Python)',
    'Understanding of networking and security principles'
  ],
  ARRAY[
    'Build and maintain CI/CD pipelines',
    'Manage cloud infrastructure and optimize costs',
    'Implement monitoring and alerting systems',
    'Automate deployment and operational tasks',
    'Respond to incidents and improve system reliability'
  ]
),
(
  '550e8400-e29b-41d4-a716-446655440006',
  'Data Analyst',
  'Data',
  'Chicago, IL (Hybrid)',
  'Full-time',
  '$80,000 - $110,000',
  'Turn data into actionable insights that drive business decisions. You''ll work with stakeholders across the company to understand their needs and deliver analytics that matter.',
  ARRAY[
    '2+ years of data analysis experience',
    'Strong SQL skills and experience with data visualization tools',
    'Proficiency in Python or R for data analysis',
    'Understanding of statistical methods',
    'Excellent presentation and storytelling skills'
  ],
  ARRAY[
    'Analyze complex datasets to identify trends and insights',
    'Create dashboards and reports for stakeholders',
    'Collaborate with teams to define metrics and KPIs',
    'Conduct A/B tests and statistical analyses',
    'Present findings to leadership and recommend actions'
  ]
);
