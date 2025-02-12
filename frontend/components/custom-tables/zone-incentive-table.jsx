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

export function ZoneIncentiveTable({ table, onTableChange }) {
  const [tableData, setTableData] = useState(table.data);

  const uniqueZones = Array.from(new Set(tableData.map((rate) => rate.zone)));

  const handleInputChange = (e, zone) => {
    const updatedTableData = tableData.map((rate) => {
      if (rate.zone === zone) {
        return { ...rate, incentive: e.target.value };
      }
      return rate;
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
                <TableHead className="w-[250px] min-w-[150px] space-x-4">
                  Zones
                </TableHead>
                {uniqueZones.map((value) => (
                  <TableHead key={value} className="text-center min-w-[80px]">
                    {value}
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium">Incentive</TableCell>
                {uniqueZones.map((zone) => {
                  const rate = tableData.find((r) => r.zone === zone);
                  return (
                    <TableCell key={zone} className="text-center">
                      <input
                        type="text"
                        value={rate ? rate.incentive : ""}
                        onChange={(e) => handleInputChange(e, zone)}
                        className="bg-transparent border-none text-gray-300 w-full text-center"
                      />
                    </TableCell>
                  );
                })}
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
