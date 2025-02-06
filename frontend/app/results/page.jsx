"use client"

import { useState } from "react"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { useAnalysis } from "@/lib/Context"

const mockData = [
  {
    serviceName: "Next Day Air Letter",
    baseRate: 45.99,
    discountedRate: 12.87,
    discountPercentage: 72,
  },
  {
    serviceName: "3 Day Select Package",
    baseRate: 32.5,
    discountedRate: 12.35,
    discountPercentage: 47,
  },
  {
    serviceName: "2nd Day Air AM CWT",
    baseRate: 28.99,
    discountedRate: 28.99,
    discountPercentage: 12,
  },
]

export default function ResultsPage() {
  const { addressDetails, parcelDetails, updateAddressDetails, updateParcelDetails, weeklyCharges } = useAnalysis()
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState({})

  const getDiscountColor = (percentage) => {
    if (percentage >= 60) return "bg-emerald-500"
    if (percentage >= 30) return "bg-orange-500"
    return "bg-red-500"
  }

  const getTextColor = (percentage) => {
    if (percentage >= 60) return "text-emerald-500"
    if (percentage >= 30) return "text-orange-500"
    return "text-red-500"
  }

  const handleInputChange = (e, category) => {
    const { name, value } = e.target
    if (category === "address") {
      updateAddressDetails({ [name]: value })
    } else if (category === "parcel") {
      updateParcelDetails({ [name]: value })
    }
  }

  const validateForm = () => {
    const errors = {}

    Object.entries(addressDetails).forEach(([key, value]) => {
      if (!value) errors[`address_${key}`] = `${key} is required`
    })

    Object.entries(parcelDetails).forEach(([key, value]) => {
      if (!value) errors[`parcel_${key}`] = `${key} is required`
    })

    setErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleUpdateAnalysis = () => {
    if (!validateForm()) return

    setLoading(true)
    // Simulating an API call
    setTimeout(() => {
      setLoading(false)
      alert("Analysis updated successfully!")
    }, 2000)
  }

  return (
    <div className="min-h-screen bg-[#1C1C28] flex items-center justify-center w-full">
      <div className="w-full max-w-6xl mx-auto px-4 py-8">
        <div className="relative w-full bg-[#23232F]/80 backdrop-blur-xl overflow-hidden rounded-2xl">
          <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-gradient-to-br from-purple-500/20 to-orange-500/20 blur-3xl rounded-full -translate-y-1/2 translate-x-1/2" />

          <div className="relative z-10 p-8 lg:p-12">
            <div className="max-w-4xl mx-auto">
              <div className="text-center mb-8">
                <h1 className="text-4xl lg:text-5xl font-bold text-white mb-3">
                  Analysis <span className="text-orange-500">Results</span>
                </h1>
                <p className="text-xl text-gray-400">Review your potential savings below</p>
              </div>

              <Card className="bg-[#2A2A36] border-gray-700 mb-6">
                <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label className="text-sm font-medium text-gray-400 mb-2 block">Address Details</Label>
                    {Object.entries(addressDetails).map(([key, value]) => (
                      <div key={key} className="mb-2">
                        <Input
                          name={key}
                          value={value}
                          onChange={(e) => handleInputChange(e, "address")}
                          className="bg-[#23232F] border-gray-600 text-white"
                          placeholder={key.charAt(0).toUpperCase() + key.slice(1)}
                        />
                        {errors[`address_${key}`] && (
                          <p className="text-red-500 text-xs mt-1">{errors[`address_${key}`]}</p>
                        )}
                      </div>
                    ))}
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-gray-400 mb-2 block">Parcel Details</Label>
                    {Object.entries(parcelDetails).map(([key, value]) => (
                      <div key={key} className="mb-2">
                        <Input
                          name={key}
                          value={value}
                          onChange={(e) => handleInputChange(e, "parcel")}
                          className="bg-[#23232F] border-gray-600 text-white"
                          placeholder={`${key.charAt(0).toUpperCase() + key.slice(1)} (${key === "weight" ? "lbs" : "in"})`}
                        />
                        {errors[`parcel_${key}`] && (
                          <p className="text-red-500 text-xs mt-1">{errors[`parcel_${key}`]}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
                <div className="px-6 pb-6">
                  <Button
                    onClick={handleUpdateAnalysis}
                    disabled={loading}
                    className="w-full bg-orange-500 hover:bg-orange-600 text-black text-lg font-semibold h-12 rounded-xl"
                  >
                    {loading ? "Updating..." : "Update Analysis"}
                  </Button>
                </div>
              </Card>

              <Card className="bg-[#2A2A36] border-gray-700">
                <div className="p-6">
                  <div className="grid grid-cols-4 gap-4 mb-4 text-sm font-medium text-gray-400 px-4">
                    <div>Service Name</div>
                    <div>Base Rate</div>
                    <div>Discounted Rate</div>
                    <div>Discount</div>
                  </div>

                  <div className="space-y-2">
                    {mockData.map((service) => (
                      <div
                        key={service.serviceName}
                        className="grid grid-cols-4 gap-4 items-center bg-[#23232F] rounded-xl p-4"
                      >
                        <div className="font-medium text-white">{service.serviceName}</div>
                        <div className="text-gray-400">${service.baseRate.toFixed(2)}</div>
                        <div className="text-gray-400">${service.discountedRate.toFixed(2)}</div>
                        <div className="flex items-center gap-3">
                          <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
                            <div
                              className={`h-full ${getDiscountColor(service.discountPercentage)} transition-all`}
                              style={{ width: `${service.discountPercentage}%` }}
                            />
                          </div>
                          <span className={`min-w-[3rem] ${getTextColor(service.discountPercentage)}`}>
                            {service.discountPercentage}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

