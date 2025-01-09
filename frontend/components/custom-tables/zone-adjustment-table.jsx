import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
  } from "@/components/ui/table"
  import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
  
  export function ZoneAdjustmentTable({ table }) {
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
                  <TableHead>Zone</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {table.data.map((adjustment, index) => (
                  <TableRow key={index}>
                    <TableCell>{adjustment.service}</TableCell>
                    <TableCell>{adjustment.zone}</TableCell>
                    <TableCell>{adjustment.incentive}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    )
  }
  
  