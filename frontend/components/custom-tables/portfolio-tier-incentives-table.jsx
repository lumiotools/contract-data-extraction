import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function PortfolioTierIncentivesTable({ table }) {
  const uniqueServices = Array.from(
    new Set(table.data.map((rate) => rate.service))
  );
  const uniqueBands = Array.from(new Set(table.data.map((rate) => rate.band)));

  return (
    <Card className="w-full mb-8">
      <CardHeader>
        <CardTitle>{table.name}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[360px]">Service</TableHead>
                <TableHead className="text-center">Land/Zone</TableHead>
                {uniqueBands.map((value) => (
                  <TableHead key={value} className="text-center min-w-[80px]">
                    {value}
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {uniqueServices.map((service) => {
                const serviceData = table.data.filter(
                  (rate) => rate.service === service
                );
                return (
                  <TableRow key={service}>
                    <TableCell className="font-medium">{service}</TableCell>

                    <TableCell className="text-center">{serviceData[0]["land/zone"]}</TableCell>

                    {uniqueBands.map((band) => {
                      const bandData = serviceData.filter(
                        (rate) => rate.band === band
                      );
                      return (
                        <TableCell key={band} className="text-center">
                          {bandData.length > 0 ? bandData[0].incentive : "-"}
                        </TableCell>
                      );
                    })}
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
