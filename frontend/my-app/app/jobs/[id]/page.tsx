import Link from "next/link";
import { notFound } from "next/navigation";
import { createServerClient } from "@/lib/supabase/server";
import { ArrowLeft, MapPin, Clock, DollarSign, Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface Job {
  id: string;
  title: string;
  department: string;
  location: string;
  type: string;
  salary_range: string;
  description: string;
  requirements: string[];
  responsibilities: string[];
  posted_date: string;
}

export default async function JobDetailPage({ params }: { params: Promise<{ id: string }> }) {
  // Await params to comply with Next.js 15
  const { id } = await params;

  const supabase = await createServerClient();

  const { data: job, error } = await supabase
    .from("jobs")
    .select("*")
    .eq("id", id)
    .eq("status", "active")
    .single();

  if (error || !job) notFound();

  const postedDate = new Date(job.posted_date).toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  });

  return (
    <div className="min-h-screen">
      <header className="border-b bg-card">
        <div className="container mx-auto px-6 py-4">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to all jobs
          </Link>
        </div>
      </header>

      <div className="container mx-auto px-6 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <Badge variant="secondary" className="mb-4">
              {job.department}
            </Badge>
            <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-4">{job.title}</h1>
            <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-1.5">
                <MapPin className="h-4 w-4" />
                <span>{job.location}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Clock className="h-4 w-4" />
                <span>{job.type}</span>
              </div>
              {job.salary_range && (
                <div className="flex items-center gap-1.5">
                  <DollarSign className="h-4 w-4" />
                  <span>{job.salary_range}</span>
                </div>
              )}
              <div className="flex items-center gap-1.5">
                <Calendar className="h-4 w-4" />
                <span>Posted {postedDate}</span>
              </div>
            </div>
          </div>

          <div className="space-y-8">
            <div className="bg-card border rounded-lg p-6">
              <h2 className="text-lg font-semibold text-foreground mb-4">About the role</h2>
              <p className="text-muted-foreground leading-relaxed">{job.description}</p>
            </div>

            <div className="bg-card border rounded-lg p-6">
              <h2 className="text-lg font-semibold text-foreground mb-4">Responsibilities</h2>
              <ul className="space-y-2">
                {job.responsibilities.map((r: string, i: number) => (
                  <li key={i} className="flex gap-3 text-muted-foreground">
                    <span className="text-primary mt-1">•</span>
                    <span>{r}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-card border rounded-lg p-6">
              <h2 className="text-lg font-semibold text-foreground mb-4">Requirements</h2>
              <ul className="space-y-2">
                {job.requirements.map((r: string, i: number) => (
                  <li key={i} className="flex gap-3 text-muted-foreground">
                    <span className="text-primary mt-1">•</span>
                    <span>{r}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="flex justify-center pt-4">
              <Link href={`/jobs/${job.id}/apply`}>
                <Button size="lg" className="px-8">
                  Apply for this position
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}