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

export function WeightZoneIncentiveTable({ table, onTableChange }) {
  const [tableData, setTableData] = useState(table.data);

  const uniqueWeights = Array.from(
    new Set(tableData.map((rate) => rate.weight))
  ).filter(Boolean);
  const uniqueZones = Array.from(new Set(tableData.map((rate) => rate.zone)));

  const handleInputChange = (e, weight, zone, field) => {
    const updatedTableData = tableData.map((rate) => {
      if (rate.weight === weight && rate.zone === zone) {
        return { ...rate, [field]: e.target.value };
      }
      return rate;
    });
    setTableData(updatedTableData);
    onTableChange({ ...table, data: updatedTableData });
  };

  const handleWeightChange = (e, oldWeight) => {
    const newWeight = e.target.value;
    const updatedTableData = tableData.map((rate) => {
      if (rate.weight === oldWeight) {
        return { ...rate, weight: newWeight };
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
                  <span>Weight (lbs)</span>
                  <span>/</span>
                  <span>Zones</span>
                </TableHead>
                {uniqueZones.map((value) => (
                  <TableHead key={value} className="text-center min-w-[80px]">
                    {value}
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {uniqueWeights.map((weight) => (
                <TableRow key={weight}>
                  <TableCell className="font-medium">
                    <input
                      type="text"
                      value={weight}
                      onChange={(e) => handleWeightChange(e, weight)}
                      className="bg-transparent border-none text-gray-300 w-full text-center"
                    />
                  </TableCell>
                  {uniqueZones.map((zone) => {
                    const rate = tableData.find(
                      (r) => r.weight === weight && r.zone === zone
                    );
                    return (
                      <TableCell key={zone} className="text-center">
                        <input
                          type="text"
                          value={rate ? rate.incentive : ""}
                          onChange={(e) => handleInputChange(e, weight, zone, 'incentive')}
                          className="bg-transparent border-none text-gray-300 w-full text-center"
                        />
                      </TableCell>
                    );
                  })}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
