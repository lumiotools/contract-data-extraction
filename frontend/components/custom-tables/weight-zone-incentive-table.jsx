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
  const [zones, setZones] = useState(Array.from(new Set(tableData.map((rate) => rate.zone))));

  const uniqueWeights = Array.from(
    new Set(tableData.map((rate) => rate.weight))
  ).filter(Boolean);

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

  const handleZoneChange = (e, index) => {
    const newZone = e.target.value;
    const updatedZones = [...zones];
    updatedZones[index] = newZone;
    setZones(updatedZones);

    const updatedTableData = tableData.map((rate) => {
      if (rate.zone === zones[index]) {
        return { ...rate, zone: newZone };
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
                {zones.map((value, index) => (
                  <TableHead key={index} className="text-center min-w-[80px]">
                    <input
                      type="text"
                      value={value}
                      onChange={(e) => handleZoneChange(e, index)}
                      className="bg-transparent border-none text-gray-300 w-full text-center"
                    />
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
                  {zones.map((zone) => {
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
