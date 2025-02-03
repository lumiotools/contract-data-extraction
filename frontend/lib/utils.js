import { clsx } from "clsx";
import { twMerge } from "tailwind-merge"

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export const incentivesData = {
  portfolio: [
    { band: "0.01 - 19429.99", incentive: 0 },
    { band: "19430.00 - 25904.99", incentive: 42 },
    { band: "25905.00 - 38859.99", incentive: 43 },
    // Add more bands as needed
  ],
  service: [
    { name: "UPS Next Day Air® - Letter", incentive: -53 },
    { name: "UPS Next Day Air®", incentive: -50 },
    // Add more services as needed
  ],
  minServiceIncentive: {
    table_type: "zone_incentive",
    name: "Service: UPS Worldwide Saver® - Export - Package - PrepaidAll - Adjustment to the 1 lb Rate Per Shipment Per Zone ($)",
    data: [
      { zone: "401", incentive: "-65.00%" },
      { zone: "402", incentive: "-65.00%" },
      { zone: "403", incentive: "-65.00%" },
      // Add more zones as needed
    ],
  },
}

export function calculateDiscounts({ weeklyCharges, zone, baseRate }) {
  const portfolioIncentive =
    incentivesData.portfolio.find(
      (p) =>
        weeklyCharges >= Number.parseFloat(p.band.split(" - ")[0]) &&
        weeklyCharges <= Number.parseFloat(p.band.split(" - ")[1]),
    )?.incentive || 0

  const discountedRate = baseRate * (1 - portfolioIncentive / 100)

  const minServiceIncentive = Number.parseFloat(
    incentivesData.minServiceIncentive.data.find((z) => z.zone === zone)?.incentive || "0",
  )

  return incentivesData.service.map((service) => {
    let finalDiscountedRate = discountedRate * (1 + service.incentive / 100)
    let appliedServiceIncentive = service.incentive

    if (service.incentive > minServiceIncentive) {
      finalDiscountedRate = discountedRate * (1 + minServiceIncentive / 100)
      appliedServiceIncentive = minServiceIncentive
    }

    return {
      serviceName: service.name,
      weeklyCharges,
      zone,
      baseRate,
      finalAmount: finalDiscountedRate,
      portfolioIncentive,
      serviceIncentive: appliedServiceIncentive,
      minServiceIncentive,
    }
  })
}



