"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { UploadIcon, Loader2, ArrowUpRight, Zap } from "lucide-react";
import { Card } from "@/components/ui/card";
import { useAnalysis } from "@/lib/Context";
import { LoadingAnimation } from "@/components/loading-animation";
import DisplayExtractedContract from "@/components/display-extracted-contract";
import { DUMMY_DATA } from "@/constants/dummyData";

export default function HomePage() {
  const router = useRouter();
  const {
    addressDetails,
    parcelDetails,
    updateAddressDetails,
    updateParcelDetails,
    weeklyCharges,
    setWeeklyCharges,
  } = useAnalysis();
  const [contractFile, setContractFile] = useState(null);
  const [isUploaded, setIsUploaded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [error, setError] = useState("");
  const [extractedContract, setExtractedContract] = useState();
  const [editableTables, setEditableTables] = useState([]);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setContractFile(file);
      setIsUploaded(true);
    }
  };

  const handleInputChange = (e, category) => {
    const { name, value } = e.target;
    if (category === "address") {
      updateAddressDetails({ [name]: value });
    } else if (category === "parcel") {
      updateParcelDetails({ [name]: value });
    } else if (name === "weeklyCharges") {
      setWeeklyCharges(value);
    }
  };

  const validateForm = () => {
    const errors = {};
    if (!contractFile) errors.contractFile = "Please upload a contract file";
    if (!weeklyCharges) errors.weeklyCharges = "Weekly charges are required";

    Object.entries(addressDetails).forEach(([key, value]) => {
      if (!value) errors[`address_${key}`] = `${key} is required`;
    });

    Object.entries(parcelDetails).forEach(([key, value]) => {
      if (!value) errors[`parcel_${key}`] = `${key} is required`;
    });

    setErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    // if (!validateForm()) return;

    setError(null);
    setLoading(true);

    const apiBaseUrl =
      process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

    try {
      const formData = new FormData();
      formData.append("file", contractFile);

      const response = await fetch(`${apiBaseUrl}/api/extract`, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem("extractedData", JSON.stringify(data.data));
        setExtractedContract(data.data);
        // setEditableTables(data.data.tables);
        setLoading(false);
      } else {
        const errorData = await response.json();
        setError(errorData.message || "An error occurred");
        setLoading(false);
      }
    } catch (error) {
      setError(error.message);
      setLoading(false);
    }
  };

  const handleTableChange = (updatedTable, index) => {
    const updatedTables = [...editableTables];
    updatedTables[index] = updatedTable;
    setEditableTables(updatedTables);

    // Retrieve existing extractedData from local storage
    const extractedData =
      JSON.parse(localStorage.getItem("extractedData")) || {};

    // Update only the tables field
    extractedData.tables = updatedTables;

    // Save the updated extractedData back to local storage
    localStorage.setItem("extractedData", JSON.stringify(extractedData));
  };

  return (
    <div className="min-h-screen bg-[#1C1C28] flex items-center justify-center w-full">
      {loading && <LoadingAnimation />}

      <div className="relative w-full bg-[#23232F]/80 backdrop-blur-xl overflow-hidden min-h-screen flex flex-col justify-center">
        <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-gradient-to-br from-purple-500/20 to-orange-500/20 blur-3xl rounded-full -translate-y-1/2 translate-x-1/2" />
        <div className="relative z-10 p-8 lg:p-12">
          <div className="max-w-3xl mx-auto">
            <Card className="bg-[#2A2A36] border-gray-700 rounded-xl">
              <form onSubmit={handleSubmit} className="p-6 space-y-6">
                <div>
                  <Label
                    htmlFor="contractFile"
                    className="text-base text-gray-300 mb-2 block"
                  >
                    Upload Contract (PDF)
                  </Label>
                  <div className="relative">
                    <label
                      htmlFor="contractFile"
                      className={`flex flex-col items-center justify-center w-full h-40 border-2 border-dashed rounded-xl cursor-pointer transition-colors ${
                        isUploaded
                          ? "border-green-500 bg-green-500/10"
                          : "border-gray-600 hover:bg-[#2A2A36]"
                      }`}
                    >
                      <div className="flex flex-col items-center justify-center py-4">
                        {isUploaded ? (
                          <>
                            <UploadIcon className="w-10 h-10 mb-2 text-green-500" />
                            <p className="text-sm text-green-500">
                              File uploaded successfully
                            </p>
                          </>
                        ) : (
                          <>
                            <UploadIcon className="w-10 h-10 mb-2 text-orange-500" />
                            <p className="text-sm text-gray-400">
                              <span className="font-semibold text-orange-500">
                                Click to upload
                              </span>{" "}
                              or drag and drop
                            </p>
                            <p className="text-xs text-gray-500 mt-1">
                              PDF (MAX. 10MB)
                            </p>
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
                    {errors.contractFile && (
                      <p className="text-red-500 text-sm mt-1">
                        {errors.contractFile}
                      </p>
                    )}
                  </div>
                </div>

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-orange-500 hover:bg-orange-600 text-black text-xl font-medium h-14 rounded-xl"
                >
                  {loading ? (
                    <Loader2 className="animate-spin mr-2" />
                  ) : (
                    "Extract Data"
                  )}
                </Button>
              </form>
              {error && (
                <div className="mb-6 bg-red-500/10 p-4 rounded-lg border border-red-500">
                  <p className="text-red-500">{error}</p>
                </div>
              )}
            </Card>

            <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="flex items-center gap-4 bg-[#2A2A36] p-4 rounded-xl">
                <div className="w-12 h-12 rounded-xl bg-orange-500/10 flex items-center justify-center">
                  <ArrowUpRight className="h-6 w-6 text-orange-500" />
                </div>
                <div>
                  <h3 className="text-lg font-medium text-white">
                    Smart Analysis
                  </h3>
                  <p className="text-sm text-gray-400">
                    AI-powered contract analysis
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-4 bg-[#2A2A36] p-4 rounded-xl">
                <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center">
                  <Zap className="h-6 w-6 text-purple-500" />
                </div>
                <div>
                  <h3 className="text-lg font-medium text-white">
                    Instant Results
                  </h3>
                  <p className="text-sm text-gray-400">
                    Get insights in seconds
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
        {extractedContract && (
          <div className="bg-[#23232F]/80 backdrop-blur-xl overflow-hidden rounded-xl p-8">
            <DisplayExtractedContract {...extractedContract} />
            {/* <DisplayTables tables={editableTables} onTableChange={handleTableChange} /> */}
            <div className="mt-8">
              <Button
                onClick={() => router.push("/results")}
                className="w-full bg-orange-500 hover:bg-orange-600 text-black text-xl font-medium h-14 rounded-xl"
              >
                Calculate Discounts
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
