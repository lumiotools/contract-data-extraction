// "use client"

// import { useState } from "react"
// import { Button } from "@/components/ui/button"
// import { Input } from "@/components/ui/input"
// import { ArrowLeft, LoaderCircle, Calculator } from "lucide-react"
// import DisplayTables from "@/components/display-tables"
// import DiscountCalculator from "@/components/discount-calculator"
// import { DUMMY_DATA } from "@/constants/dummyData"

// const HomePage = () => {
//   const [tables, setTables] = useState()
//   const [loading, setLoading] = useState(false)
//   const [file, setFile] = useState()
//   const [showCalculator, setShowCalculator] = useState(false)

//   const handlePdfUpload = async () => {
//     setLoading(true)
//     try {
//       if (!file) throw new Error("Please select a file to upload")
//       const formData = new FormData()
//       formData.append("file", file)

//       const response = await (
//         await fetch(process.env.NEXT_PUBLIC_API_URL + "/api/extract", {
//           method: "POST",
//           body: formData,
//         })
//       ).json()

//       if (!response.success) throw new Error(response.message)

//       setTables(response.tables)
//     } catch (error) {
//       alert(error.message)
//     }
//     setLoading(false)
//   }

//   const handleBack = () => {
//     if (showCalculator) {
//       setShowCalculator(false)
//     } else {
//       setTables(undefined)
//     }
//   }

//   return (
//     <div className="container p-8">
//       {!tables && !showCalculator ? (
//         <div className="space-y-8">
//           <div className="flex justify-center items-center gap-4">
//             <Input
//               type="file"
//               accept="application/pdf"
//               onChange={(e) => setFile(e.target.files[0])}
//               disabled={loading}
//             />
//             <Button disabled={loading} onClick={handlePdfUpload}>
//               {loading && <LoaderCircle className="mr-2 h-4 w-4 animate-spin" />}
//               Upload PDF & Extract
//             </Button>
//           </div>
//           <div className="flex justify-center gap-4">
//             <Button onClick={() => setTables(DUMMY_DATA.tables)} disabled={loading}>
//               View Sample Extracted Data
//             </Button>
//             <Button onClick={() => setShowCalculator(true)} disabled={loading}>
//               <Calculator className="mr-2 h-4 w-4" />
//               Open Discount Calculator
//             </Button>
//           </div>
//         </div>
//       ) : (
//         <>
//           <Button onClick={handleBack} className="mb-4">
//             <ArrowLeft className="mr-2 h-4 w-4" />
//             Back
//           </Button>
//           {showCalculator ? <DiscountCalculator /> : <DisplayTables tables={tables} />}
//         </>
//       )}
//     </div>
//   )
// }

// export default HomePage

"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { UploadIcon, Loader2, ArrowUpRight, Zap } from "lucide-react"
import { Card } from "@/components/ui/card"
import { useAnalysis } from "@/lib/Context"

export default function HomePage() {
  const router = useRouter()
  const { addressDetails, parcelDetails, updateAddressDetails, updateParcelDetails, weeklyCharges, setWeeklyCharges } = useAnalysis()
  const [contractFile, setContractFile] = useState(null)
  // const [weeklyCharges, setWeeklyCharges] = useState("")
  const [isUploaded, setIsUploaded] = useState(false)
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState({})

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setContractFile(file)
      setIsUploaded(true)
    }
  }

  const handleInputChange = (e, category) => {
    const { name, value } = e.target
    if (category === "address") {
      updateAddressDetails({ [name]: value })
    } else if (category === "parcel") {
      updateParcelDetails({ [name]: value })
    } else if (name === "weeklyCharges") {
      setWeeklyCharges(value)
    }
  }

  const validateForm = () => {
    const errors = {}
    if (!contractFile) errors.contractFile = "Please upload a contract file"
    if (!weeklyCharges) errors.weeklyCharges = "Weekly charges are required"

    Object.entries(addressDetails).forEach(([key, value]) => {
      if (!value) errors[`address_${key}`] = `${key} is required`
    })

    Object.entries(parcelDetails).forEach(([key, value]) => {
      if (!value) errors[`parcel_${key}`] = `${key} is required`
    })

    setErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;
  
    setLoading(true);
  
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
  
    try {
      const response = await fetch(`${apiBaseUrl}/api/extract`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ 
          
          weeklyCharges,
          addressDetails,
          parcelDetails,
        }),
      });
  
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem("extractedData", JSON.stringify(data)); // Save response to localStorage
        router.push("/results");
      } else {
        console.error("Error: Extraction API failed", response.statusText);
      }
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  };
  
  

  return (
    <div className="min-h-screen bg-[#1C1C28] flex items-center justify-center w-full">
      <div className="w-full max-w-6xl mx-auto px-4 py-8">
        <div className="relative w-full bg-[#23232F]/80 backdrop-blur-xl overflow-hidden rounded-2xl">
          <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-gradient-to-br from-purple-500/20 to-orange-500/20 blur-3xl rounded-full -translate-y-1/2 translate-x-1/2" />

          <div className="relative z-10 p-8 lg:p-12">
            <div className="max-w-3xl mx-auto">
              {/* <div className="text-center mb-8">
                <h1 className="text-4xl lg:text-5xl font-bold text-white mb-3">
                  Smart Contract <span className="text-orange-500">Analysis</span>
                </h1>
                <p className="text-xl text-gray-400">Upload your contract and provide details for instant analysis</p>
              </div> */}

              <Card className="bg-[#2A2A36] border-gray-700">
                <form onSubmit={handleSubmit} className="p-6 space-y-6">
                  {/* File upload section */}
                  <div>
                    <Label htmlFor="contractFile" className="text-base text-gray-300 mb-2 block">
                      Upload Contract (PDF)
                    </Label>
                    <div className="relative">
                      <label
                        htmlFor="contractFile"
                        className={`flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-xl cursor-pointer transition-colors ${
                          isUploaded ? "border-green-500 bg-green-500/10" : "border-gray-600 hover:bg-[#2A2A36]"
                        }`}
                      >
                        <div className="flex flex-col items-center justify-center py-4">
                          {isUploaded ? (
                            <>
                              <UploadIcon className="w-10 h-10 mb-2 text-green-500" />
                              <p className="text-sm text-green-500">File uploaded successfully</p>
                            </>
                          ) : (
                            <>
                              <UploadIcon className="w-10 h-10 mb-2 text-orange-500" />
                              <p className="text-sm text-gray-400">
                                <span className="font-semibold text-orange-500">Click to upload</span> or drag and drop
                              </p>
                              <p className="text-xs text-gray-500 mt-1">PDF (MAX. 10MB)</p>
                            </>
                          )}
                        </div>
                        <Input
                          id="contractFile"
                          type="file"
                          accept=".pdf"
                          className="hidden"
                          onChange={handleFileChange}
                        />
                      </label>
                      {errors.contractFile && <p className="text-red-500 text-sm mt-1">{errors.contractFile}</p>}
                    </div>
                  </div>

                  {/* Weekly charges input */}
                  <div className="space-y-1">
                    <Label htmlFor="weeklyCharges" className="text-base text-gray-300 block">
                      Weekly Charges ($)
                    </Label>
                    <Input
                      id="weeklyCharges"
                      name="weeklyCharges"
                      type="number"
                      placeholder="Enter weekly charges"
                      value={weeklyCharges}
                      onChange={handleInputChange}
                      className="bg-[#23232F] border-gray-600 text-white placeholder:text-gray-500"
                    />
                    {errors.weeklyCharges && <p className="text-red-500 text-xs">{errors.weeklyCharges}</p>}
                  </div>

                  {/* Address details inputs */}
                  <div className="space-y-4">
                    <Label className="text-base text-gray-300 block">Destination Address</Label>
                    <div className="grid grid-cols-2 gap-4">
                      {Object.entries(addressDetails).map(([key, value]) => (
                        <div key={key} className="space-y-1">
                          <Input
                            name={key}
                            placeholder={key.charAt(0).toUpperCase() + key.slice(1)}
                            value={value}
                            onChange={(e) => handleInputChange(e, "address")}
                            className="bg-[#23232F] border-gray-600 text-white placeholder:text-gray-500"
                          />
                          {errors[`address_${key}`] && (
                            <p className="text-red-500 text-xs">{errors[`address_${key}`]}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Parcel details inputs */}
                  <div className="space-y-4">
                    <Label className="text-base text-gray-300 block">Parcel Details</Label>
                    <div className="grid grid-cols-2 gap-4">
                      {Object.entries(parcelDetails).map(([key, value]) => (
                        <div key={key} className="space-y-1">
                          <Input
                            name={key}
                            placeholder={`${key.charAt(0).toUpperCase() + key.slice(1)} (${key === "weight" ? "lbs" : "in"})`}
                            type="number"
                            value={value}
                            onChange={(e) => handleInputChange(e, "parcel")}
                            className="bg-[#23232F] border-gray-600 text-white placeholder:text-gray-500"
                          />
                          {errors[`parcel_${key}`] && <p className="text-red-500 text-xs">{errors[`parcel_${key}`]}</p>}
                        </div>
                      ))}
                    </div>
                  </div>

                  <Button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-orange-500 hover:bg-orange-600 text-black text-lg font-semibold h-14 rounded-xl"
                  >
                    {loading ? <Loader2 className="animate-spin mr-2" /> : "Submit and check discount rates"}
                  </Button>
                </form>
              </Card>

              {/* Feature highlights */}
              <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="flex items-center gap-4 bg-[#2A2A36] p-4 rounded-xl">
                  <div className="w-12 h-12 rounded-xl bg-orange-500/10 flex items-center justify-center">
                    <ArrowUpRight className="h-6 w-6 text-orange-500" />
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-white">Smart Analysis</h3>
                    <p className="text-sm text-gray-400">AI-powered contract analysis</p>
                  </div>
                </div>
                <div className="flex items-center gap-4 bg-[#2A2A36] p-4 rounded-xl">
                  <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center">
                    <Zap className="h-6 w-6 text-purple-500" />
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-white">Instant Results</h3>
                    <p className="text-sm text-gray-400">Get insights in seconds</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}





