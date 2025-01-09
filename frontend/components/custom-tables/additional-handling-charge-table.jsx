import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
  } from "@/components/ui/table"
  import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
  
  export function AdditionalHandlingChargeTable({ table }) {
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
                  <TableHead>Land/Zone</TableHead>
                  <TableHead>Incentives</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {table.data.map((charge, index) => (
                  <TableRow key={index}>
                    <TableCell>{charge.service}</TableCell>
                    <TableCell>{charge["land/zone"]}</TableCell>
                    <TableCell>{charge.incentives}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    )
  }
  
  