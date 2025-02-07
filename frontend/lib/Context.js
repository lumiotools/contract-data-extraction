"use client"

import { createContext, useState, useContext, useEffect } from "react"

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

  useEffect(()=>{
    const formData = JSON.parse(localStorage.getItem("formData"));

    if(formData){
      setAddressDetails(formData.addressDetails);
      setParcelDetails(formData.parcelDetails);
      setWeeklyCharges(formData.weeklyCharges);
    }
  },[])

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

