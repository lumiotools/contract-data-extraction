"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { useAnalysis } from "@/lib/Context";
import { Loader2, Package, DollarSign, TrendingUp, MapPin } from "lucide-react";

export default function ResultsPage() {
  const {
    addressDetails,
    parcelDetails,
    weeklyCharges,
    updateAddressDetails,
    updateParcelDetails,
    setWeeklyCharges,
  } = useAnalysis();
  const [loading, setLoading] = useState(false);
  const [discountData, setDiscountData] = useState(null);
  const [error, setError] = useState(null);
  const [activateCalculateButton, setActivateCalculateButton] = useState(true);

  useEffect(() => {
    if (discountData) return;
    if (!addressDetails.street || !parcelDetails.weight || !weeklyCharges)
      return;
    const fetchData = async () => {
      setActivateCalculateButton(false);
      setLoading(true);
      setError(null);
      try {
        const extractedData = JSON.parse(
          localStorage.getItem("extractedData") || "{}"
        );
        const apiData = {
          weekly_price: Number.parseFloat(weeklyCharges),
          start_address: {
            street: extractedData?.source_address?.street || "",
            city: extractedData?.source_address?.city || "",
            state: extractedData?.source_address?.stateCode || "",
            zip: extractedData?.source_address?.zipCode || "",
            country: extractedData?.source_address?.countryCode || "",
          },
          destination_address: {
            street: addressDetails.street,
            city: addressDetails.city,
            state: addressDetails.stateCode,
            zip: addressDetails.zipCode,
            country: addressDetails.countryCode,
          },
          parcel: {
            weight: Number.parseFloat(parcelDetails.weight),
            length: Number.parseFloat(parcelDetails.length),
            width: Number.parseFloat(parcelDetails.width),
            height: Number.parseFloat(parcelDetails.height),
          },
          tables_json: JSON.stringify({ tables: extractedData.tables } || []),
          contract_type: extractedData.contract_type || "ups",
        };

        const apiBaseUrl =
          process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
        const response = await fetch(`${apiBaseUrl}/calculate_discount`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(apiData),
        });

        if (!response.ok) throw new Error("Failed to calculate discounts");
        const data = await response.json();
        setDiscountData(data.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    // fetchData();
  }, [addressDetails, parcelDetails, weeklyCharges, discountData]);

  const handleAddressChange = (e) => {
    setActivateCalculateButton(true);
    updateAddressDetails({ [e.target.name]: e.target.value });
  };

  const handleParcelChange = (e) => {
    setActivateCalculateButton(true);
    updateParcelDetails({ [e.target.name]: e.target.value });
  };

  const handleWeeklyChargesChange = (e) => {
    setActivateCalculateButton(true);
    setWeeklyCharges(e.target.value);
  };

  const calculateDiscounts = async () => {
    setLoading(true);
    setError(null);
    try {
      const extractedData = JSON.parse(
        localStorage.getItem("extractedData") || "{}"
      );
      const apiData = {
        weekly_price: Number.parseFloat(weeklyCharges),
        start_address: {
          street: extractedData?.source_address?.street || "",
          city: extractedData?.source_address?.city || "",
          state: extractedData?.source_address?.stateCode || "",
          zip: extractedData?.source_address?.zipCode || "",
          country: extractedData?.source_address?.countryCode || "",
        },
        destination_address: {
          street: addressDetails.street,
          city: addressDetails.city,
          state: addressDetails.stateCode,
          zip: addressDetails.zipCode,
          country: addressDetails.countryCode,
        },
        parcel: {
          weight: Number.parseFloat(parcelDetails.weight),
          length: Number.parseFloat(parcelDetails.length),
          width: Number.parseFloat(parcelDetails.width),
          height: Number.parseFloat(parcelDetails.height),
        },
        tables_json: JSON.stringify({ tables: extractedData.tables } || []),
        contract_type: extractedData.contract_type || "ups",
      };

      const apiBaseUrl =
        process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
      const response = await fetch(`${apiBaseUrl}/calculate_discount`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(apiData),
      });

      if (!response.ok) throw new Error("Failed to calculate discounts");
      const data = await response.json();
      setDiscountData(data.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setActivateCalculateButton(false);
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
      {/* <div className="w-full max-w-6xl mx-auto px-4 py-8"> */}
      <div className="relative w-full min-h-screen bg-[#23232F]/80 backdrop-blur-xl overflow-hidden flex flex-col justify-center items-center">
        <div className="absolute top-0 right-0 w-[800px] min-h-screen bg-gradient-to-br from-purple-500/20 to-orange-500/20 blur-3xl rounded-full -translate-y-1/2 translate-x-1/2 " />
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

            <Card className="bg-[#2A2A36] border-gray-700 mb-6 rounded-xl">
              <div className="p-6 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="flex items-center gap-2 mb-4">
                      <MapPin className="w-5 h-5 text-purple-500" />
                      <h3 className="text-lg font-semibold text-white">
                        Destination Address
                      </h3>
                    </div>
                    <div>
                      <Label className="text-gray-400 block mb-2">Street</Label>
                      <Input
                        name="street"
                        value={addressDetails.street}
                        onChange={handleAddressChange}
                        className="bg-[#23232F] border-gray-600 text-white"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-gray-400 block mb-2">City</Label>
                        <Input
                          name="city"
                          value={addressDetails.city}
                          onChange={handleAddressChange}
                          className="bg-[#23232F] border-gray-600 text-white"
                        />
                      </div>
                      <div>
                        <Label className="text-gray-400 block mb-2">
                          State
                        </Label>
                        <Input
                          name="stateCode"
                          value={addressDetails.stateCode}
                          onChange={handleAddressChange}
                          className="bg-[#23232F] border-gray-600 text-white"
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-gray-400 block mb-2">
                          ZIP Code
                        </Label>
                        <Input
                          name="zipCode"
                          value={addressDetails.zipCode}
                          onChange={handleAddressChange}
                          className="bg-[#23232F] border-gray-600 text-white"
                        />
                      </div>
                      <div>
                        <Label className="text-gray-400 block mb-2">
                          Country
                        </Label>
                        <Input
                          name="countryCode"
                          value={addressDetails.countryCode}
                          onChange={handleAddressChange}
                          className="bg-[#23232F] border-gray-600 text-white"
                        />
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="flex items-center gap-3 mb-4">
                      <Package className="w-5 h-5 text-purple-500" />
                      <h3 className="text-lg font-semibold text-white">
                        Parcel Details
                      </h3>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-gray-400 block mb-2">
                          Weight (lbs)
                        </Label>
                        <Input
                          name="weight"
                          value={parcelDetails.weight}
                          onChange={handleParcelChange}
                          className="bg-[#23232F] border-gray-600 text-white"
                        />
                      </div>
                      <div>
                        <Label className="text-gray-400 block mb-2">
                          Length (inches)
                        </Label>
                        <Input
                          name="length"
                          value={parcelDetails.length}
                          onChange={handleParcelChange}
                          className="bg-[#23232F] border-gray-600 text-white"
                        />
                      </div>
                      <div>
                        <Label className="text-gray-400 block mb-2">
                          Width (inches)
                        </Label>
                        <Input
                          name="width"
                          value={parcelDetails.width}
                          onChange={handleParcelChange}
                          className="bg-[#23232F] border-gray-600 text-white"
                        />
                      </div>
                      <div>
                        <Label className="text-gray-400 block mb-2">
                          Height (inches)
                        </Label>
                        <Input
                          name="height"
                          value={parcelDetails.height}
                          onChange={handleParcelChange}
                          className="bg-[#23232F] border-gray-600 text-white"
                        />
                      </div>
                    </div>
                    <div>
                      <Label className="text-gray-400 block mb-2">
                        Weekly Charges ($)
                      </Label>
                      <Input
                        name="weeklyCharges"
                        value={weeklyCharges}
                        onChange={handleWeeklyChargesChange}
                        className="bg-[#23232F] border-gray-600 text-white"
                      />
                    </div>
                  </div>
                </div>

                <div>
                  <Button
                    onClick={calculateDiscounts}
                    disabled={!activateCalculateButton && loading}
                    className={`w-full ${
                      activateCalculateButton
                        ? `bg-orange-500 hover:bg-orange-600 text-black`
                        : `bg-gray-500 hover:bg-gray-500 text-white cursor-not-allowed`
                    } text-lg font-semibold h-12 rounded-xl`}
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
              </div>
            </Card>

            {error && (
              <div className="mb-6 bg-red-500/10 p-4 rounded-lg border border-red-500">
                <p className="text-red-500">Error: {error}</p>
              </div>
            )}

            {discountData && (
              <>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                  <Card className="bg-[#2A2A36] border-gray-700 rounded-xl">
                    <div className="p-6">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center">
                          <Package className="w-6 h-6 text-purple-500" />
                        </div>
                        <div>
                          <p className="text-sm text-gray-400">Weekly Volume</p>
                          <p className="text-xl font-semibold text-white">
                            ${weeklyCharges}
                          </p>
                        </div>
                      </div>
                    </div>
                  </Card>
                  <Card className="bg-[#2A2A36] border-gray-700 rounded-xl">
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
                            {(
                              discountData.reduce(
                                (sum, service) =>
                                  sum + service.service_discount,
                                0
                              ) / discountData.length
                            ).toFixed(2)}
                            %
                          </p>
                        </div>
                      </div>
                    </div>
                  </Card>
                  <Card className="bg-[#2A2A36] border-gray-700 rounded-xl">
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
                            {Math.max(
                              ...discountData.map(
                                (service) => service.service_discount
                              )
                            ).toFixed(2)}
                            %
                          </p>
                        </div>
                      </div>
                    </div>
                  </Card>
                </div>

                <Card className="bg-[#2A2A36] border-gray-700 rounded-xl">
                  <div className="p-6">
                    <div className="grid grid-cols-6 gap-4 mb-4 text-sm font-medium text-gray-400 px-4">
                      <div className="col-span-2">Service Name</div>
                      <div className="text-center">Actual Rate</div>
                      <div className="text-center">Rate after Discount</div>
                      <div className="text-center">Discount</div>
                      <div className="text-center">Minimum ?</div>
                    </div>

                    <div className="space-y-2">
                      {discountData.map((service, index) => (
                        <div
                          key={index}
                          className="grid grid-cols-6 gap-4 items-center bg-[#23232F] rounded-xl p-4"
                        >
                          <div className="col-span-2 font-medium text-white">
                            {service.service_name}
                            {service.is_over_discounted && (
                              <span
                                className="bg-[#499D822E] ml-2 border border-[#0FBA82] rounded-[6px] px-[10px] py-[4px] text-green-600 text-xs font-medium"
                                style={{ width: "57px", height: "29px" }}
                              >
                                BEST
                              </span>
                            )}
                          </div>
                          <div className="text-gray-400 text-center">
                            {service.base_amount ? service.base_amount : "-"}
                          </div>
                          <div className="text-gray-400 text-center">
                            {service.final_amount ? service.final_amount : "-"}
                          </div>
                          <div className="flex items-center gap-3">
                            <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
                              <div
                                className={`h-full ${getDiscountColor(
                                  service.service_discount
                                )} transition-all`}
                                style={{
                                  width: `${service.service_discount}%`,
                                }}
                              />
                            </div>
                            <span
                              className={`min-w-[3rem] ${getTextColor(
                                service.service_discount
                              )}`}
                            >
                              {service.service_discount.toFixed(2)}%
                            </span>
                          </div>
                          <div className="text-gray-400 text-center">
                            {service.is_over_discounted ? "TRUE" : "FALSE"}
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
      {/* </div> */}
    </div>
  );
}
