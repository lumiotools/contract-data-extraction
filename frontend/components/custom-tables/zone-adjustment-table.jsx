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

export function ZoneAdjustmentTable({ table, onTableChange }) {
  const [tableData, setTableData] = useState(table.data);

  const handleInputChange = (e, index, field) => {
    const updatedTableData = tableData.map((adjustment, i) => {
      if (i === index) {
        return { ...adjustment, [field]: e.target.value };
      }
      return adjustment;
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
                <TableHead>Zone</TableHead>
                <TableHead>Service</TableHead>
                <TableHead>Incentive</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {tableData.map((adjustment, index) => (
                <TableRow key={index}>
                  <TableCell>
                    <input
                      type="text"
                      value={adjustment.zone}
                      onChange={(e) => handleInputChange(e, index, 'zone')}
                      className="bg-transparent border-none text-gray-300 w-full"
                    />
                  </TableCell>
                  <TableCell>
                    <input
                      type="text"
                      value={adjustment.service}
                      onChange={(e) => handleInputChange(e, index, 'service')}
                      className="bg-transparent border-none text-gray-300 w-full"
                    />
                  </TableCell>
                  <TableCell>
                    <input
                      type="text"
                      value={adjustment.incentive}
                      onChange={(e) => handleInputChange(e, index, 'incentive')}
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

