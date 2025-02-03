"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ArrowLeft, LoaderCircle, Calculator } from "lucide-react"
import DisplayTables from "@/components/display-tables"
import DiscountCalculator from "@/components/discount-calculator"
import { DUMMY_DATA } from "@/constants/dummyData"

const HomePage = () => {
  const [tables, setTables] = useState()
  const [loading, setLoading] = useState(false)
  const [file, setFile] = useState()
  const [showCalculator, setShowCalculator] = useState(false)

  const handlePdfUpload = async () => {
    setLoading(true)
    try {
      if (!file) throw new Error("Please select a file to upload")
      const formData = new FormData()
      formData.append("file", file)

      const response = await (
        await fetch(process.env.NEXT_PUBLIC_API_URL + "/api/extract", {
          method: "POST",
          body: formData,
        })
      ).json()

      if (!response.success) throw new Error(response.message)

      setTables(response.tables)
    } catch (error) {
      alert(error.message)
    }
    setLoading(false)
  }

  const handleBack = () => {
    if (showCalculator) {
      setShowCalculator(false)
    } else {
      setTables(undefined)
    }
  }

  return (
    <div className="container p-8">
      {!tables && !showCalculator ? (
        <div className="space-y-8">
          <div className="flex justify-center items-center gap-4">
            <Input
              type="file"
              accept="application/pdf"
              onChange={(e) => setFile(e.target.files[0])}
              disabled={loading}
            />
            <Button disabled={loading} onClick={handlePdfUpload}>
              {loading && <LoaderCircle className="mr-2 h-4 w-4 animate-spin" />}
              Upload PDF & Extract
            </Button>
          </div>
          <div className="flex justify-center gap-4">
            <Button onClick={() => setTables(DUMMY_DATA.tables)} disabled={loading}>
              View Sample Extracted Data
            </Button>
            <Button onClick={() => setShowCalculator(true)} disabled={loading}>
              <Calculator className="mr-2 h-4 w-4" />
              Open Discount Calculator
            </Button>
          </div>
        </div>
      ) : (
        <>
          <Button onClick={handleBack} className="mb-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
          {showCalculator ? <DiscountCalculator /> : <DisplayTables tables={tables} />}
        </>
      )}
    </div>
  )
}

export default HomePage

