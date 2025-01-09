import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function ServiceMinPerZoneBaseRateAdjustmentTable({ table }) {
  return (
    <Card className="w-full mb-8">
      <CardHeader>
        <CardTitle>
          {table.name || "Service Minimum Per Zone Base Rate Adjustment"}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Service</TableHead>
                <TableHead>Min Per</TableHead>
                <TableHead>Zone</TableHead>
                <TableHead>Base Rate</TableHead>
                <TableHead>Adjustment</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {table.data.map((adjustment, index) => (
                <TableRow key={index}>
                  <TableCell>{adjustment.service}</TableCell>
                  <TableCell>{adjustment.min_per || "-"}</TableCell>
                  <TableCell>{adjustment.zone || "-"}</TableCell>
                  <TableCell>{adjustment.base_rate || "-"}</TableCell>
                  <TableCell>{adjustment.adjustment || "-"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
