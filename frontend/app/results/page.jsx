"use client";

import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { useAnalysis } from "@/lib/Context";
import {
  Loader2,
  Package,
  DollarSign,
  TrendingUp,
  Building,
} from "lucide-react";

export default function ResultsPage() {
  const { addressDetails, parcelDetails, weeklyCharges } = useAnalysis();
  const [loading, setLoading] = useState(false);
  const [discountData, setDiscountData] = useState(null);
  const [error, setError] = useState(null);

  // Start address state
  const [startAddress, setStartAddress] = useState({
    street: "UPS HQ",
    city: "Atlanta",
    state: "GA",
    zip: "30328",
    country: "USA",
  });

  // Handle start address input changes
  const handleStartAddressChange = (e) => {
    const { name, value } = e.target;
    setStartAddress((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const calculateDiscounts = async () => {
    setLoading(true);
    setError(null);

    try {
      // Get tables from extractedData in localStorage
      const extractedData = JSON.parse(
        localStorage.getItem("extractedData") || "{}"
      );

      const apiData = {
        weekly_price: parseFloat(weeklyCharges),
        start_address: startAddress,
        destination_address: {
          street: addressDetails.street,
          city: addressDetails.city,
          state: addressDetails.stateCode,
          zip: addressDetails.zipCode,
          country: addressDetails.countryCode,
        },
        parcel: {
          weight: parseFloat(parcelDetails.weight),
          length: parseFloat(parcelDetails.length),
          width: parseFloat(parcelDetails.width),
          height: parseFloat(parcelDetails.height),
        },
        tables_json: JSON.stringify(extractedData.tables || []),
        contract_type: extractedData.contract_type || "ups",
      };

      const apiBaseUrl =
        process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

      const response = await fetch(`${apiBaseUrl}/calculate_discount`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(apiData),
      });

      if (!response.ok) {
        throw new Error("Failed to calculate discounts");
      }

      const data = await response.json();
      setDiscountData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getDiscountColor = (percentage) => {
    if (percentage >= 60) return "bg-emerald-500";
    if (percentage >= 30) return "bg-orange-500";
    return "bg-red-500";
  };

  const getTextColor = (percentage) => {
    if (percentage >= 60) return "text-emerald-500";
    if (percentage >= 30) return "text-orange-500";
    return "text-red-500";
  };

  return (
    <div className="min-h-screen bg-[#1C1C28] flex items-center justify-center w-full">
      <div className="w-full max-w-6xl mx-auto px-4 py-8">
        <div className="relative w-full bg-[#23232F]/80 backdrop-blur-xl overflow-hidden rounded-2xl">
          <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-gradient-to-br from-purple-500/20 to-orange-500/20 blur-3xl rounded-full -translate-y-1/2 translate-x-1/2" />

          <div className="relative z-10 p-8 lg:p-12">
            <div className="max-w-4xl mx-auto">
              <div className="text-center mb-8">
                <h1 className="text-4xl lg:text-5xl font-bold text-white mb-3">
                  Shipping <span className="text-orange-500">Details</span>
                </h1>
                <p className="text-xl text-gray-400">
                  Review and calculate your discounts
                </p>
              </div>

              {/* Address Details */}
              <Card className="bg-[#2A2A36] border-gray-700 mb-6">
                <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Start Address */}
                  <div>
                    <div className="flex items-center gap-3 mb-4">
                      <Building className="w-5 h-5 text-orange-500" />
                      <h3 className="text-lg font-semibold text-white">
                        Start Address
                      </h3>
                    </div>
                    <div className="space-y-3">
                      <div>
                        <Label className="text-gray-400">Street</Label>
                        <Input
                          name="street"
                          value={startAddress.street}
                          onChange={handleStartAddressChange}
                          className="bg-[#23232F] border-gray-600 text-white"
                        />
                      </div>
                      <div>
                        <Label className="text-gray-400">City</Label>
                        <Input
                          name="city"
                          value={startAddress.city}
                          onChange={handleStartAddressChange}
                          className="bg-[#23232F] border-gray-600 text-white"
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <Label className="text-gray-400">State</Label>
                          <Input
                            name="state"
                            value={startAddress.state}
                            onChange={handleStartAddressChange}
                            className="bg-[#23232F] border-gray-600 text-white"
                          />
                        </div>
                        <div>
                          <Label className="text-gray-400">ZIP</Label>
                          <Input
                            name="zip"
                            value={startAddress.zip}
                            onChange={handleStartAddressChange}
                            className="bg-[#23232F] border-gray-600 text-white"
                          />
                        </div>
                      </div>
                      <div>
                        <Label className="text-gray-400">Country</Label>
                        <Input
                          name="country"
                          value={startAddress.country}
                          onChange={handleStartAddressChange}
                          className="bg-[#23232F] border-gray-600 text-white"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Destination Address */}
                  <div>
                    <div className="flex items-center gap-3 mb-4">
                      <Package className="w-5 h-5 text-purple-500" />
                      <h3 className="text-lg font-semibold text-white">
                        Destination Address
                      </h3>
                    </div>
                    <div className="space-y-2">
                      <p className="text-gray-400">{addressDetails.street}</p>
                      <p className="text-gray-400">
                        {addressDetails.city}, {addressDetails.stateCode}{" "}
                        {addressDetails.zipCode}
                      </p>
                      <p className="text-gray-400">
                        {addressDetails.countryCode}
                      </p>
                    </div>

                    <div className="mt-6">
                      <h3 className="text-lg font-semibold text-white mb-4">
                        Parcel Details
                      </h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm text-gray-400">Weight</p>
                          <p className="text-white">
                            {parcelDetails.weight} lbs
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-400">Dimensions</p>
                          <p className="text-white">
                            {parcelDetails.length}" × {parcelDetails.width}" ×{" "}
                            {parcelDetails.height}"
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="px-6 pb-6">
                  <Button
                    onClick={calculateDiscounts}
                    disabled={loading}
                    className="w-full bg-orange-500 hover:bg-orange-600 text-black text-lg font-semibold h-12 rounded-xl"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Calculating...
                      </>
                    ) : (
                      "Calculate Discounts"
                    )}
                  </Button>
                </div>
              </Card>

              {error && (
                <div className="mb-6 bg-red-500/10 p-4 rounded-lg border border-red-500">
                  <p className="text-red-500">Error: {error}</p>
                </div>
              )}

              {discountData && (
                <>
                  {/* Summary Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <Card className="bg-[#2A2A36] border-gray-700">
                      <div className="p-6">
                        <div className="flex items-center gap-4">
                          <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center">
                            <Package className="w-6 h-6 text-purple-500" />
                          </div>
                          <div>
                            <p className="text-sm text-gray-400">
                              Weekly Volume
                            </p>
                            <p className="text-xl font-semibold text-white">
                              ${weeklyCharges}
                            </p>
                          </div>
                        </div>
                      </div>
                    </Card>
                    <Card className="bg-[#2A2A36] border-gray-700">
                      <div className="p-6">
                        <div className="flex items-center gap-4">
                          <div className="w-12 h-12 rounded-xl bg-orange-500/10 flex items-center justify-center">
                            <DollarSign className="w-6 h-6 text-orange-500" />
                          </div>
                          <div>
                            <p className="text-sm text-gray-400">
                              Average Savings
                            </p>
                            <p className="text-xl font-semibold text-white">
                              {discountData?.averageSavings || "32"}%
                            </p>
                          </div>
                        </div>
                      </div>
                    </Card>
                    <Card className="bg-[#2A2A36] border-gray-700">
                      <div className="p-6">
                        <div className="flex items-center gap-4">
                          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center">
                            <TrendingUp className="w-6 h-6 text-emerald-500" />
                          </div>
                          <div>
                            <p className="text-sm text-gray-400">
                              Best Service Savings
                            </p>
                            <p className="text-xl font-semibold text-white">
                              {discountData?.bestSavings || "42"}%
                            </p>
                          </div>
                        </div>
                      </div>
                    </Card>
                  </div>

                  {/* Discount Table */}
                  <Card className="bg-[#2A2A36] border-gray-700">
                    <div className="p-6">
                      <div className="grid grid-cols-4 gap-4 mb-4 text-sm font-medium text-gray-400 px-4">
                        <div>Service Name</div>
                        <div>Base Rate</div>
                        <div>Your Rate</div>
                        <div>Savings</div>
                      </div>

                      <div className="space-y-2">
                        {(
                          discountData?.services || [
                            {
                              name: "Next Day Air Letter",
                              baseRate: 45.99,
                              discountedRate: 12.87,
                              savingsPercent: 72,
                            },
                            {
                              name: "3 Day Select Package",
                              baseRate: 32.5,
                              discountedRate: 12.35,
                              savingsPercent: 47,
                            },
                            {
                              name: "2nd Day Air AM CWT",
                              baseRate: 28.99,
                              discountedRate: 28.99,
                              savingsPercent: 12,
                            },
                          ]
                        ).map((service) => (
                          <div
                            key={service.name}
                            className="grid grid-cols-4 gap-4 items-center bg-[#23232F] rounded-xl p-4"
                          >
                            <div className="font-medium text-white">
                              {service.name}
                            </div>
                            <div className="text-gray-400">
                              ${service.baseRate.toFixed(2)}
                            </div>
                            <div className="text-gray-400">
                              ${service.discountedRate.toFixed(2)}
                            </div>
                            <div className="flex items-center gap-3">
                              <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
                                <div
                                  className={`h-full ${getDiscountColor(
                                    service.savingsPercent
                                  )} transition-all`}
                                  style={{
                                    width: `${service.savingsPercent}%`,
                                  }}
                                />
                              </div>
                              <span
                                className={`min-w-[3rem] ${getTextColor(
                                  service.savingsPercent
                                )}`}
                              >
                                {service.savingsPercent}%
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </Card>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
