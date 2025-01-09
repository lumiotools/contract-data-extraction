import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function ZoneIncentiveTable({ table }) {
  const uniqueZones = Array.from(new Set(table.data.map((rate) => rate.zone)));

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
                <TableHead className="w-[250px] min-w-[150px] space-x-4">
                  Zones
                </TableHead>

                {uniqueZones.map((value) => (
                  <TableHead key={value} className="text-center min-w-[80px]">
                    {value}
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium">Incentive</TableCell>
                {uniqueZones.map((zone) => {
                  const rate = table.data.find((r) => r.zone === zone);
                  return (
                    <TableCell key={zone} className="text-center">
                      {rate ? rate.incentive : "-"}
                    </TableCell>
                  );
                })}
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
