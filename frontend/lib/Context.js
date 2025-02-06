"use client"

import { createContext, useState, useContext } from "react"

const AnalysisContext = createContext()

export const AnalysisProvider = ({ children }) => {
  const [addressDetails, setAddressDetails] = useState({
    street: "",
    city: "",
    stateCode: "",
    zipCode: "",
    countryCode: "",
  })
  const [parcelDetails, setParcelDetails] = useState({
    weight: "",
    length: "",
    height: "",
    width: "",
  })

  const [weeklyCharges, setWeeklyCharges] = useState("");

  const updateAddressDetails = (newDetails) => {
    setAddressDetails((prev) => ({ ...prev, ...newDetails }))
  }

  const updateParcelDetails = (newDetails) => {
    setParcelDetails((prev) => ({ ...prev, ...newDetails }))
  }

  return (
    <AnalysisContext.Provider
      value={{
        addressDetails,
        parcelDetails,
        weeklyCharges,
        updateAddressDetails,
        updateParcelDetails,
        setWeeklyCharges
      }}
    >
      {children}
    </AnalysisContext.Provider>
  )
}

export const useAnalysis = () => useContext(AnalysisContext)

