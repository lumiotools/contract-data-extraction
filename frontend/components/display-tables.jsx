import { ServiceIncentivesTable } from "@/components/custom-tables/service-incentives-table";
import { PortfolioTierIncentivesTable } from "@/components/custom-tables/portfolio-tier-incentives-table";
import { ServiceMinPerZoneBaseRateAdjustmentTable } from "@/components/custom-tables/service-min-per-zone-base-rate-adjustment-table";
import { AdditionalHandlingChargeTable } from "@/components/custom-tables/additional-handling-charge-table";
import { ElectronicPLDBonusTable } from "@/components/custom-tables/electronic-pld-bonus-table";
import { ZoneAdjustmentTable } from "@/components/custom-tables/zone-adjustment-table";
import { WeightZoneIncentiveTable } from "./custom-tables/weight-zone-incentive-table";
import { ZoneBandsIncentiveTable } from "./custom-tables/zone-bands-incentive-table";
import { ZoneIncentiveTable } from "./custom-tables/zone-incentive-table";
import { DestinationZoneIncentiveTable } from "./custom-tables/destination-zone-incentive-table";
import { DestinationZoneWeightIncentiveTable } from "./custom-tables/destination-zone-weight-incentive-table";

export default function DisplayTables({ tables, onTableChange }) {
  return (
    <div className="space-y-8 text-white">
      {tables.map((table, index) => {
        switch (table.table_type) {
          case "weight_zone_incentive":
            return (
              <WeightZoneIncentiveTable
                key={index}
                table={table}
                onTableChange={(updatedTable) => onTableChange(updatedTable, index)}
              />
            );
          case "zone_bands_incentive":
            return (
              <ZoneBandsIncentiveTable
                key={index}
                table={table}
                onTableChange={(updatedTable) => onTableChange(updatedTable, index)}
              />
            );
          case "zone_incentive":
            return (
              <ZoneIncentiveTable
                key={index}
                table={table}
                onTableChange={(updatedTable) => onTableChange(updatedTable, index)}
              />
            );
          case "destination_zone_incentive":
            return (
              <DestinationZoneIncentiveTable
                key={index}
                table={table}
                onTableChange={(updatedTable) => onTableChange(updatedTable, index)}
              />
            );
          case "destination_zone_weight_incentive":
            return (
              <DestinationZoneWeightIncentiveTable
                key={index}
                table={table}
                onTableChange={(updatedTable) => onTableChange(updatedTable, index)}
              />
            );
          case "service_incentives":
            return (
              <ServiceIncentivesTable
                key={index}
                table={table}
                onTableChange={(updatedTable) => onTableChange(updatedTable, index)}
              />
            );
          case "portfolio_tier_incentives":
            return (
              <PortfolioTierIncentivesTable
                key={index}
                table={table}
                onTableChange={(updatedTable) => onTableChange(updatedTable, index)}
              />
            );
          case "service_min_per_zone_base_rate_adjustment":
            return (
              <ServiceMinPerZoneBaseRateAdjustmentTable
                key={index}
                table={table}
                onTableChange={(updatedTable) => onTableChange(updatedTable, index)}
              />
            );
          case "additional_handling_charge":
            return (
              <AdditionalHandlingChargeTable
                key={index}
                table={table}
                onTableChange={(updatedTable) => onTableChange(updatedTable, index)}
              />
            );
          case "electronic_pld_bonus":
            return (
              <ElectronicPLDBonusTable
                key={index}
                table={table}
                onTableChange={(updatedTable) => onTableChange(updatedTable, index)}
              />
            );
          case "zone_incentive_min_charge":
            return (
              <ZoneIncentiveTable
                key={index}
                table={table}
                onTableChange={(updatedTable) => onTableChange(updatedTable, index)}
              />
            );
          default:
            return null;
        }
      })}
    </div>
  );
}
