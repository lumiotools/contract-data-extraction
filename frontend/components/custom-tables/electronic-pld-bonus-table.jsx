import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function ElectronicPLDBonusTable({ table }) {
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
                <TableHead>Service</TableHead>
                <TableHead>Electronic PLD Bonus</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {table.data.map((bonus, index) => (
                <TableRow key={index}>
                  <TableCell>{bonus.service}</TableCell>
                  <TableCell>{bonus.electronic_pld_bonus}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
