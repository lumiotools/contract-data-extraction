import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
  } from "@/components/ui/table"
  import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
  
  export function ServiceIncentivesTable({ table }) {
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
                  <TableHead>Incentive</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {table.data.map((incentive, index) => (
                  <TableRow key={index}>
                    <TableCell>{incentive.service}</TableCell>
                    <TableCell>{incentive.incentive}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    )
  }
  
  