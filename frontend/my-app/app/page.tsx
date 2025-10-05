import Link from "next/link"
import { createServerClient } from "@/lib/supabase/server"
import { Briefcase, MapPin, Clock } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

interface Job {
  id: string
  title: string
  department: string
  location: string
  type: string
  salary_range: string
  description: string
}

export default async function HomePage() {
  const supabase = await createServerClient()

  const { data: jobs, error } = await supabase
    .from("jobs")
    .select("*")
    .eq("status", "active")
    .order("posted_date", { ascending: false })

  if (error) {
    console.error("[v0] Error fetching jobs:", error)
  }

  // Group jobs by department
  const jobsByDepartment = (jobs || []).reduce(
    (acc, job) => {
      if (!acc[job.department]) {
        acc[job.department] = []
      }
      acc[job.department].push(job)
      return acc
    },
    {} as Record<string, Job[]>,
  )

  const departments = Object.keys(jobsByDepartment).sort()

  return (
    <div className="min-h-screen">
      <header className="border-b bg-card">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Briefcase className="h-6 w-6 text-primary" />
              <span className="text-xl font-semibold">TechCorp Careers</span>
            </div>
            <nav className="flex items-center gap-6">
              <Link href="/" className="text-sm font-medium text-foreground hover:text-primary transition-colors">
                Jobs
              </Link>
              <Link
                href="#"
                className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                About
              </Link>
              <Link
                href="#"
                className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                Culture
              </Link>
            </nav>
          </div>
        </div>
      </header>

      <section className="bg-card border-b">
        <div className="container mx-auto px-6 py-16 md:py-24">
          <div className="max-w-3xl">
            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4 tracking-tight">Join our team</h1>
            <p className="text-lg text-muted-foreground leading-relaxed mb-8">
              We're building the future of technology. Explore open positions and find your next opportunity with us.
            </p>
            <div className="flex items-center gap-6 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <Briefcase className="h-4 w-4" />
                <span>{jobs?.length || 0} open positions</span>
              </div>
              <div className="flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                <span>Multiple locations</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="container mx-auto px-6 py-12">
        {departments.length === 0 ? (
          <div className="text-center py-16">
            <p className="text-muted-foreground">No open positions at the moment. Check back soon!</p>
          </div>
        ) : (
          <div className="space-y-12">
            {departments.map((department) => (
              <div key={department}>
                <div className="flex items-center gap-3 mb-6">
                  <h2 className="text-xl font-semibold text-foreground">{department}</h2>
                  <Badge variant="secondary" className="text-xs">
                    {jobsByDepartment[department].length}
                  </Badge>
                </div>
                <div className="space-y-3">
                    {jobsByDepartment[department].map((job: Job) => (
                    <Link key={job.id} href={`/jobs/${job.id}`}>
                      <div className="bg-card border rounded-lg p-6 hover:border-primary/50 hover:shadow-sm transition-all">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1 min-w-0">
                            <h3 className="text-lg font-semibold text-foreground mb-2">{job.title}</h3>
                            <p className="text-sm text-muted-foreground mb-4 line-clamp-2">{job.description}</p>
                            <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                              <div className="flex items-center gap-1.5">
                                <MapPin className="h-4 w-4" />
                                <span>{job.location}</span>
                              </div>
                              <div className="flex items-center gap-1.5">
                                <Clock className="h-4 w-4" />
                                <span>{job.type}</span>
                              </div>
                              {job.salary_range && (
                                <div className="font-medium text-foreground">{job.salary_range}</div>
                              )}
                            </div>
                          </div>
                          <Button variant="outline" size="sm" className="shrink-0 bg-transparent">
                            View Details
                          </Button>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      <footer className="border-t mt-20 bg-card">
        <div className="container mx-auto px-6 py-8">
          <p className="text-center text-sm text-muted-foreground">© 2025 TechCorp. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
