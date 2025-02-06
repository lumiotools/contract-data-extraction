"use client";

import { useState } from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { DUMMY_DATA } from "@/constants/dummyData";

const schema = z.object({
  weeklyCharges: z.number().positive("Weekly charges must be positive"),
  destinationAddress: z.string().min(1, "Destination address is required"),
});

// Sample data matching the expected API response format
// const sampleData = [
//   {
//     service_name: "UPS Worldwide Express® - Export - Letter - PrepaidAll",
//     portfolio_incentive_applied: "42.0%",
//     service_incentive_applied: "-53.0%",
//     discounted_amount: 473.0,
//     zone_incentive_applied: "-68.0%",
//     zone_incentive_amount: 321.64,
//     final_amount: 151.36,
//   },
//   {
//     service_name: "UPS Worldwide Express® - Export - Package - PrepaidAll",
//     portfolio_incentive_applied: "42.0%",
//     service_incentive_applied: "-50.0%",
//     discounted_amount: 490.0,
//     zone_incentive_applied: "-65.0%",
//     zone_incentive_amount: 318.5,
//     final_amount: 171.5,
//   },
//   {
//     service_name: "UPS Worldwide Saver® - Export - Letter - PrepaidAll",
//     portfolio_incentive_applied: "42.0%",
//     service_incentive_applied: "-55.0%",
//     discounted_amount: 464.0,
//     zone_incentive_applied: "-70.0%",
//     zone_incentive_amount: 324.8,
//     final_amount: 139.2,
//   },
// ]

export default function DiscountCalculator() {
  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(schema),
  });
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const onSubmit = async (data) => {
    setIsLoading(true);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/calculate_discount`,
        {
          // mode:"no-cors",
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            weekly_price: data.weeklyCharges,
            destination_address: data.destinationAddress,
            tables_json: JSON.stringify(DUMMY_DATA),
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const calculationResults = await response.json();
      console.log("Response", calculationResults);
      setResults(calculationResults.data);

      // await new Promise((resolve) => setTimeout(resolve, 1000))

      // // Filter sample data based on weekly charges (for demonstration purposes)
      // const filteredResults = sampleData.map((item) => ({
      //   ...item,
      //   discounted_amount: item.discounted_amount * (data.weeklyCharges / 1000),
      //   zone_incentive_amount: item.zone_incentive_amount * (data.weeklyCharges / 1000),
      //   final_amount: item.final_amount * (data.weeklyCharges / 1000),
      // }))

      // setResults(filteredResults)
    } catch (error) {
      console.error("Error calculating discounts:", error);
      setResults([{ error: error.message }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-6xl mx-auto">
      <CardHeader>
        <CardTitle>Discount Calculator</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 mb-6">
          <div>
            <Label htmlFor="weeklyCharges">Weekly Charges ($)</Label>
            <Controller
              name="weeklyCharges"
              control={control}
              render={({ field }) => (
                <Input
                  id="weeklyCharges"
                  type="number"
                  step="0.01"
                  {...field}
                  onChange={(e) =>
                    field.onChange(Number.parseFloat(e.target.value))
                  }
                  aria-invalid={errors.weeklyCharges ? "true" : "false"}
                />
              )}
            />
            {errors.weeklyCharges && (
              <p className="text-destructive text-sm mt-1">
                {errors.weeklyCharges.message}
              </p>
            )}
          </div>
          <div>
            <Label htmlFor="destinationAddress">Destination Address</Label>
            <Controller
              name="destinationAddress"
              control={control}
              render={({ field }) => (
                <Input
                  id="destinationAddress"
                  type="text"
                  {...field}
                  aria-invalid={errors.destinationAddress ? "true" : "false"}
                />
              )}
            />
            {errors.destinationAddress && (
              <p className="text-destructive text-sm mt-1">
                {errors.destinationAddress.message}
              </p>
            )}
          </div>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? "Calculating..." : "Calculate"}
          </Button>
        </form>

        {results && results[0] && !results[0].error && (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Service Name</TableHead>
                  <TableHead>Discount</TableHead>
                  <TableHead>Is Minimum Rate Reached</TableHead>
                  <TableHead>Base Amount ($)</TableHead>
                  <TableHead>Final Amount ($)</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {results.map((result, index) => (
                  <TableRow key={index}>
                    <TableCell>{result.service_name}</TableCell>
                    <TableCell>
                      {result.service_discount?.toFixed(2) ?? "-"}%
                    </TableCell>
                    <TableCell>
                      {result.is_over_discounted ? "Yes" : "No"}
                    </TableCell>
                    <TableCell>
                      {result.base_amount?.toFixed(2) ?? "-"}
                    </TableCell>
                    <TableCell>
                      {result.final_amount?.toFixed(2) ?? "-"}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}

        {results && results[0] && results[0].error && (
          <Alert className="mt-4">
            <AlertDescription>
              <span className="text-destructive">{results[0].error}</span>
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}
