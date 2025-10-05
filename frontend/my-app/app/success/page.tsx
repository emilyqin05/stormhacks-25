"use client"

import { useSearchParams } from "next/navigation"
import { CheckCircle2, Briefcase } from "lucide-react"
import { Suspense } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"

function SuccessContent() {
  const searchParams = useSearchParams()
  const applicantId = searchParams.get("id")
  const jobTitle = searchParams.get("job")

  return (
    <div className="min-h-screen">
      <header className="border-b bg-card">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center gap-2">
            <Briefcase className="h-6 w-6 text-primary" />
            <span className="text-xl font-semibold">TechCorp Careers</span>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-16">
        <div className="max-w-2xl mx-auto">
          <div className="bg-card border rounded-lg p-8 md:p-12">
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-primary/10 rounded-full mb-6">
                <CheckCircle2 className="w-8 h-8 text-primary" />
              </div>
              <h1 className="text-3xl font-bold text-foreground mb-3">Application submitted successfully</h1>
              <p className="text-muted-foreground">
                {jobTitle ? `Thank you for applying to ${jobTitle}` : "Thank you for your interest in joining our team"}
              </p>
            </div>

            <div className="bg-muted/50 border rounded-lg p-6 mb-8">
              <p className="text-sm font-medium text-foreground mb-2">Application ID</p>
              <p className="text-base font-mono text-foreground break-all">{applicantId}</p>
            </div>

            <div className="space-y-4 mb-8 text-sm text-muted-foreground">
              <p>
                We've received your application and our team will review it carefully. You can expect to hear back from
                us within 5 business days.
              </p>
              <p>
                A confirmation email has been sent to the address you provided. Please save your Application ID for
                future reference.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-3">
              <Link href="/" className="flex-1">
                <Button className="w-full">View more positions</Button>
              </Link>
              <Link href="/" className="flex-1">
                <Button variant="outline" className="w-full bg-transparent">
                  Back to homepage
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function SuccessPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      }
    >
      <SuccessContent />
    </Suspense>
  )
}
