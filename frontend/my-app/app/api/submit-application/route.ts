import { type NextRequest, NextResponse } from "next/server"
import { Storage } from "@google-cloud/storage"
import { createClient } from "@supabase/supabase-js"

// Initialize Google Cloud Storage
const storage = new Storage({
  projectId: process.env.GCS_PROJECT_ID,
  credentials: JSON.parse(process.env.GCP_KEY_JSON!)
})

const bucketName = process.env.GCS_BUCKET_NAME!

// Create Supabase admin client with service role key to bypass RLS
// This is safe for server-side API routes as the key is never exposed to the client
const supabaseAdmin = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!,
  {
    auth: {
      autoRefreshToken: false,
      persistSession: false
    }
  }
)

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const name = formData.get("name") as string
    const email = formData.get("email") as string
    const resume = formData.get("resume") as File
    const jobId = formData.get("jobId") as string

    // Validate inputs
    if (!name || !email || !resume || !jobId) {
      return NextResponse.json({ error: "Missing required fields" }, { status: 400 })
    }

    // Validate file type
    const allowedTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "application/msword",
    ]
    if (!allowedTypes.includes(resume.type)) {
      return NextResponse.json({ error: "Only PDF and DOCX files are allowed" }, { status: 400 })
    }

    // Generate unique applicant ID
    const applicantId = crypto.randomUUID()

    // Create filename with applicant ID
    const fileExtension = resume.name.split(".").pop()
    const fileName = `${applicantId}.${fileExtension}`

    // Upload to Google Cloud Storage
    const bucket = storage.bucket(bucketName)
    const file = bucket.file(fileName)

    // Convert File to Buffer
    const arrayBuffer = await resume.arrayBuffer()
    const buffer = Buffer.from(arrayBuffer)

    // Upload file
    await file.save(buffer, {
      metadata: {
        contentType: resume.type,
      },
    })

    // Get public URL
    const resumeUrl = `https://storage.googleapis.com/${bucketName}/${fileName}`

    // Insert into database using admin client (bypasses RLS)
    const { data, error } = await supabaseAdmin
      .from("applicants")
      .insert({
        applicant_id: applicantId,
        job_id: jobId,
        name,
        email,
        resume_url: resumeUrl,
      })
      .select()
      .single()

    if (error) {
      console.error("[v0] Database error:", error)
      return NextResponse.json({ error: "Failed to save application" }, { status: 500 })
    }

    return NextResponse.json({
      success: true,
      applicantId: data.applicant_id,
      message: "Application submitted successfully",
    })
  } catch (error) {
    console.error("[v0] Application submission error:", error)
    return NextResponse.json({ error: "Failed to process application" }, { status: 500 })
  }
}