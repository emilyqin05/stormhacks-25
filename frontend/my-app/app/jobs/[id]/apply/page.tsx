import { notFound } from "next/navigation";
import { createServerClient } from "@/lib/supabase/server";
import Link from "next/link";
import { ArrowLeft, Briefcase } from "lucide-react";
import { ApplicationForm } from "@/components/application-form";

export default async function ApplyPage({ params }: { params: Promise<{ id: string }> }) {
  // Await params to comply with Next.js 15 async dynamic route rules
  const { id } = await params;

  const supabase = await createServerClient();

  const { data: job, error } = await supabase
    .from("jobs")
    .select("id, title, department, location")
    .eq("id", id)
    .eq("status", "active")
    .single();

  if (error || !job) {
    notFound();
  }

  return (
    <div className="min-h-screen">
      <header className="border-b bg-card">
        <div className="container mx-auto px-6 py-4">
          <Link
            href={`/jobs/${job.id}`}
            className="inline-flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to job details
          </Link>
        </div>
      </header>

      <div className="container mx-auto px-6 py-12">
        <div className="max-w-2xl mx-auto">
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-primary/10 rounded-lg">
                <Briefcase className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-foreground">Apply for {job.title}</h1>
                <p className="text-sm text-muted-foreground">
                  {job.department} • {job.location}
                </p>
              </div>
            </div>
            <p className="text-sm text-muted-foreground">
              Fill out the form below to submit your application. We'll review it and get back to you within 5 business
              days.
            </p>
          </div>

          {/* Pass the correct jobId so ApplicationForm inserts into applicants.job_id */}
          <ApplicationForm jobId={job.id} jobTitle={job.title} />
        </div>
      </div>
    </div>
  );
}