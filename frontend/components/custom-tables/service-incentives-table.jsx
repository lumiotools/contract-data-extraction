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

export function ServiceIncentivesTable({ table, onTableChange }) {
  const [tableData, setTableData] = useState(table.data);

  const handleInputChange = (e, index, field) => {
    const updatedTableData = tableData.map((incentive, i) => {
      if (i === index) {
        return { ...incentive, [field]: e.target.value };
      }
      return incentive;
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
                <TableHead>Incentive</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {tableData.map((incentive, index) => (
                <TableRow key={index}>
                  <TableCell>
                    <input
                      type="text"
                      value={incentive.service}
                      onChange={(e) => handleInputChange(e, index, 'service')}
                      className="bg-transparent border-none text-gray-300 w-full"
                    />
                  </TableCell>
                  <TableCell>
                    <input
                      type="text"
                      value={incentive.incentive}
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

