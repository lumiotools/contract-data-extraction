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

export function ElectronicPLDBonusTable({ table, onTableChange }) {
  const [tableData, setTableData] = useState(table.data);

  const handleInputChange = (e, index, field) => {
    const updatedTableData = tableData.map((bonus, i) => {
      if (i === index) {
        return { ...bonus, [field]: e.target.value };
      }
      return bonus;
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
                <TableHead>Electronic PLD Bonus</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {tableData.map((bonus, index) => (
                <TableRow key={index}>
                  <TableCell>
                    <input
                      type="text"
                      value={bonus.service}
                      onChange={(e) => handleInputChange(e, index, 'service')}
                      className="bg-transparent border-none text-gray-300 w-full"
                    />
                  </TableCell>
                  <TableCell>
                    <input
                      type="text"
                      value={bonus.electronic_pld_bonus}
                      onChange={(e) => handleInputChange(e, index, 'electronic_pld_bonus')}
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
