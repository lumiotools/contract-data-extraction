import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function ZoneBandsIncentiveTable({ table }) {
  const uniqueZones = Array.from(new Set(table.data.map((rate) => rate.zone)));
  const uniqueBands = Array.from(
    new Set(table.data.map((rate) => rate.band))
  ).filter(Boolean);

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
                  
                      <span>Zone</span>
                      <span>/</span>
                      <span>Bands ($)</span>
                    
                </TableHead>

                {uniqueBands.map(
                  (value) => (
                    <TableHead key={value} className="text-center min-w-[80px]">
                      {value}
                    </TableHead>
                  )
                )}
              </TableRow>
            </TableHeader>
            <TableBody>
              {uniqueZones.map((zone) => (
                <TableRow key={zone}>
                  <TableCell className="font-medium">{zone}</TableCell>
                  {uniqueBands.map((band) => {
                    const rate = table.data.find(
                      (r) => r.band === band && r.zone === zone
                    );
                    return (
                      <TableCell key={band} className="text-center">
                        {rate ? rate.incentive : "-"}
                      </TableCell>
                    );
                  })}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
