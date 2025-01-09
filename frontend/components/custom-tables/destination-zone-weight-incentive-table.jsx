import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function DestinationZoneWeightIncentiveTable({ table }) {
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
                <TableHead className="text-center">Destination</TableHead>
                <TableHead className="text-center">Zone</TableHead>
                <TableHead className="text-center">Weight (lbs)</TableHead>
                <TableHead className="text-center">Incentives</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {table.data.map((rate, index) => (
                <TableRow key={index}>
                  <TableCell className="text-center">
                    {rate.destination}
                  </TableCell>
                  <TableCell className="text-center">{rate.zone}</TableCell>
                  <TableCell className="text-center">{rate.weight}</TableCell>
                  <TableCell className="text-center">{rate.incentive}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
