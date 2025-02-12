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

export function DestinationZoneWeightIncentiveTable({ table, onTableChange }) {
  const [tableData, setTableData] = useState(table.data);

  const handleInputChange = (e, index, field) => {
    const updatedTableData = tableData.map((rate, i) => {
      if (i === index) {
        return { ...rate, [field]: e.target.value };
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
                <TableHead className="text-center">Destination</TableHead>
                <TableHead className="text-center">Zone</TableHead>
                <TableHead className="text-center">Weight (lbs)</TableHead>
                <TableHead className="text-center">Incentives</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {tableData.map((rate, index) => (
                <TableRow key={index}>
                  <TableCell className="text-center">
                    <input
                      type="text"
                      value={rate.destination}
                      onChange={(e) => handleInputChange(e, index, 'destination')}
                      className="bg-transparent border-none text-gray-300 w-full text-center"
                    />
                  </TableCell>
                  <TableCell className="text-center">
                    <input
                      type="text"
                      value={rate.zone}
                      onChange={(e) => handleInputChange(e, index, 'zone')}
                      className="bg-transparent border-none text-gray-300 w-full text-center"
                    />
                  </TableCell>
                  <TableCell className="text-center">
                    <input
                      type="text"
                      value={rate.weight}
                      onChange={(e) => handleInputChange(e, index, 'weight')}
                      className="bg-transparent border-none text-gray-300 w-full text-center"
                    />
                  </TableCell>
                  <TableCell className="text-center">
                    <input
                      type="text"
                      value={rate.incentive}
                      onChange={(e) => handleInputChange(e, index, 'incentive')}
                      className="bg-transparent border-none text-gray-300 w-full text-center"
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
