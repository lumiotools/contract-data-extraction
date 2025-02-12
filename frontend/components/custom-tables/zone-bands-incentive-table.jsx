import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function ZoneBandsIncentiveTable({ table, onTableChange }) {
  const [tableData, setTableData] = useState(table.data);
  const [bands, setBands] = useState(Array.from(new Set(tableData.map((rate) => rate.band))).filter(Boolean));

  const uniqueZones = Array.from(new Set(tableData.map((rate) => rate.zone)));

  const handleInputChange = (e, zone, band) => {
    const updatedTableData = tableData.map((rate) => {
      if (rate.zone === zone && rate.band === band) {
        return { ...rate, incentive: e.target.value };
      }
      return rate;
    });
    setTableData(updatedTableData);
    onTableChange({ ...table, data: updatedTableData });
  };

  const handleBandChange = (e, index) => {
    const newBand = e.target.value;
    const updatedBands = [...bands];
    updatedBands[index] = newBand;
    setBands(updatedBands);

    const updatedTableData = tableData.map((rate) => {
      if (rate.band === bands[index]) {
        return { ...rate, band: newBand };
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
                  <span>Zone</span>
                  <span>/</span>
                  <span>Bands ($)</span>
                </TableHead>
                {bands.map((value, index) => (
                  <TableHead key={index} className="text-center min-w-[80px]">
                    <div className="flex flex-col items-center">
                      <input
                        type="text"
                        value={value}
                        onChange={(e) => handleBandChange(e, index)}
                        className="bg-transparent border-none text-gray-300 w-full text-center"
                      />
                    </div>
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {uniqueZones.map((zone) => (
                <TableRow key={zone}>
                  <TableCell className="font-medium">{zone}</TableCell>
                  {bands.map((band) => {
                    const rate = tableData.find(
                      (r) => r.band === band && r.zone === zone
                    );
                    return (
                      <TableCell key={band} className="text-center">
                        <input
                          type="text"
                          value={rate ? rate.incentive : ""}
                          onChange={(e) => handleInputChange(e, zone, band)}
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
