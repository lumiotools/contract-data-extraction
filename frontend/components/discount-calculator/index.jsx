"use client"

import { useState } from "react"
import { useForm, Controller } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

const schema = z.object({
  weeklyCharges: z.number().positive("Weekly charges must be positive"),
  zone: z.string().min(1, "Zone is required"),
  baseRate: z.number().positive("Base rate must be positive"),
})

const zones = ["401", "402", "403"] // Add more zones as needed

// Sample data
const sampleResults = [
  {
    service_name: "UPS Worldwide Express® - Export - Letter - PrepaidAll",
    portfolio_tier_incentive_applied: "42.0%",
    service_incentive_applied: "-53.0%",
    total_incentive_applied: "-11.0%",
    discounted_amount: 473.0,
    zone_incentive_applied: "-68.0%",
    final_amount: 473.0,
  },
  {
    service_name: "UPS Worldwide Express® - Export - Package - PrepaidAll",
    portfolio_tier_incentive_applied: "42.0%",
    service_incentive_applied: "-50.0%",
    total_incentive_applied: "-8.0%",
    discounted_amount: 490.0,
    zone_incentive_applied: "-65.0%",
    final_amount: 490.0,
  },
]

export default function DiscountCalculator() {
  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(schema),
  })
  const [results, setResults] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const onSubmit = async (data) => {
    setIsLoading(true)
    try {
      // Commented out API call
      // const response = await fetch('/api/calculate-discounts', {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //   },
      //   body: JSON.stringify(data),
      // })

      // if (!response.ok) {
      //   throw new Error('Failed to calculate discounts')
      // }

      // const calculationResults = await response.json()
      // setResults(calculationResults)

      // Using sample data instead
      setResults(sampleResults)
    } catch (error) {
      console.error("Error calculating discounts:", error)
      setResults([{ error: error.message }])
    } finally {
      setIsLoading(false)
    }
  }

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
                  onChange={(e) => field.onChange(Number.parseFloat(e.target.value))}
                  aria-invalid={errors.weeklyCharges ? "true" : "false"}
                />
              )}
            />
            {errors.weeklyCharges && <p className="text-destructive text-sm mt-1">{errors.weeklyCharges.message}</p>}
          </div>

          <div>
            <Label htmlFor="zone">Zone</Label>
            <Controller
              name="zone"
              control={control}
              render={({ field }) => (
                <Select onValueChange={field.onChange} defaultValue={field.value}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select a zone" />
                  </SelectTrigger>
                  <SelectContent>
                    {zones.map((zone) => (
                      <SelectItem key={zone} value={zone}>
                        {zone}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            />
            {errors.zone && <p className="text-destructive text-sm mt-1">{errors.zone.message}</p>}
          </div>

          <div>
            <Label htmlFor="baseRate">Base Rate ($)</Label>
            <Controller
              name="baseRate"
              control={control}
              render={({ field }) => (
                <Input
                  id="baseRate"
                  type="number"
                  step="0.01"
                  {...field}
                  onChange={(e) => field.onChange(Number.parseFloat(e.target.value))}
                  aria-invalid={errors.baseRate ? "true" : "false"}
                />
              )}
            />
            {errors.baseRate && <p className="text-destructive text-sm mt-1">{errors.baseRate.message}</p>}
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
                  <TableHead>Portfolio Tier Incentive</TableHead>
                  <TableHead>Service Incentive</TableHead>
                  <TableHead>Total Incentive</TableHead>
                  <TableHead>Discounted Amount ($)</TableHead>
                  <TableHead>Zone Incentive</TableHead>
                  <TableHead>Final Amount ($)</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {results.map((result, index) => (
                  <TableRow key={index}>
                    <TableCell>{result.service_name}</TableCell>
                    <TableCell>{result.portfolio_tier_incentive_applied}</TableCell>
                    <TableCell>{result.service_incentive_applied}</TableCell>
                    <TableCell>{result.total_incentive_applied}</TableCell>
                    <TableCell>{result.discounted_amount.toFixed(2)}</TableCell>
                    <TableCell>{result.zone_incentive_applied}</TableCell>
                    <TableCell>{result.final_amount.toFixed(2)}</TableCell>
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
  )
}

