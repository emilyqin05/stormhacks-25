"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Upload, Loader2, FileText, X } from "lucide-react"

interface ApplicationFormProps {
  jobId: string
  jobTitle: string
}

export function ApplicationForm({ jobId, jobTitle }: ApplicationFormProps) {
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file type
    const validTypes = [
      "application/pdf",
      "application/msword",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]
    if (!validTypes.includes(file.type)) {
      setError("Please upload a PDF or DOCX file")
      setSelectedFile(null)
      return
    }

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      setError("File size must be less than 5MB")
      setSelectedFile(null)
      return
    }

    setError(null)
    setSelectedFile(file)
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError(null)

    const formData = new FormData(e.currentTarget)

    if (!selectedFile) {
      setError("Please upload your resume")
      setIsSubmitting(false)
      return
    }

    formData.append("resume", selectedFile)
    formData.append("jobId", jobId)

    try {
      const response = await fetch("/api/submit-application", {
        method: "POST",
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || "Failed to submit application")
      }

      // Redirect to success page with applicant ID
      router.push(`/success?id=${data.applicantId}&job=${encodeURIComponent(jobTitle)}`)
    } catch (err) {
      console.error("[v0] Application submission error:", err)
      setError(err instanceof Error ? err.message : "Failed to submit application")
      setIsSubmitting(false)
    }
  }

  return (
    <div className="bg-card border rounded-lg p-8">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="name" className="text-sm font-medium">
            Full Name
          </Label>
          <Input
            id="name"
            name="name"
            type="text"
            required
            placeholder="Enter your full name"
            disabled={isSubmitting}
            className="h-10"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="email" className="text-sm font-medium">
            Email Address
          </Label>
          <Input
            id="email"
            name="email"
            type="email"
            required
            placeholder="you@example.com"
            disabled={isSubmitting}
            className="h-10"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="resume" className="text-sm font-medium">
            Resume
          </Label>
          <div className="relative">
            <label
              htmlFor="resume"
              className="flex items-center justify-center gap-2 h-32 border-2 border-dashed rounded-lg cursor-pointer hover:border-primary/50 transition-colors bg-muted/30"
            >
              {selectedFile ? (
                <div className="flex items-center gap-3">
                  <FileText className="h-5 w-5 text-primary" />
                  <div className="text-left">
                    <p className="text-sm font-medium text-foreground">{selectedFile.name}</p>
                    <p className="text-xs text-muted-foreground">{(selectedFile.size / 1024).toFixed(1)} KB</p>
                  </div>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.preventDefault()
                      setSelectedFile(null)
                    }}
                    className="ml-2 p-1 hover:bg-muted rounded"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              ) : (
                <div className="text-center">
                  <Upload className="h-6 w-6 text-muted-foreground mx-auto mb-2" />
                  <p className="text-sm font-medium text-foreground">Click to upload resume</p>
                  <p className="text-xs text-muted-foreground mt-1">PDF or DOCX (Max 5MB)</p>
                </div>
              )}
            </label>
            <Input
              id="resume"
              name="resume"
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={handleFileChange}
              disabled={isSubmitting}
              className="sr-only"
            />
          </div>
        </div>

        {error && (
          <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
            <p className="text-sm text-destructive">{error}</p>
          </div>
        )}

        <Button type="submit" disabled={isSubmitting || !selectedFile} className="w-full h-10" size="lg">
          {isSubmitting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Submitting application...
            </>
          ) : (
            "Submit application"
          )}
        </Button>

        <p className="text-xs text-center text-muted-foreground">
          By submitting this application, you agree to our privacy policy and terms of service.
        </p>
      </form>
    </div>
  )
}
