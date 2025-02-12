import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function AdditionalHandlingChargeTable({ table, onTableChange }) {
  const [tableData, setTableData] = useState(table.data);

  const handleInputChange = (e, index, field) => {
    const updatedTableData = tableData.map((charge, i) => {
      if (i === index) {
        return { ...charge, [field]: e.target.value };
      }
      return charge;
    });
    setTableData(updatedTableData);
    onTableChange({ ...table, data: updatedTableData });
  };

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
              {tableData.map((charge, index) => (
                <TableRow key={index}>
                  <TableCell>
                    <input
                      type="text"
                      value={charge.service}
                      onChange={(e) => handleInputChange(e, index, 'service')}
                      className="bg-transparent border-none text-gray-300 w-full"
                    />
                  </TableCell>
                  <TableCell>
                    <input
                      type="text"
                      value={charge["land/zone"]}
                      onChange={(e) => handleInputChange(e, index, 'land/zone')}
                      className="bg-transparent border-none text-gray-300 w-full"
                    />
                  </TableCell>
                  <TableCell>
                    <input
                      type="text"
                      value={charge.incentives}
                      onChange={(e) => handleInputChange(e, index, 'incentives')}
                      className="bg-transparent border-none text-gray-300 w-full"
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}

