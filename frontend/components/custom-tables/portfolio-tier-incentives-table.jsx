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

export function PortfolioTierIncentivesTable({ table, onTableChange }) {
  const [tableData, setTableData] = useState(table.data);
  const [bands, setBands] = useState(Array.from(new Set(tableData.map((rate) => rate.band))).filter(Boolean));
  const [activeBandIndex, setActiveBandIndex] = useState(null);
  const [activeServiceIndex, setActiveServiceIndex] = useState(null);

  const uniqueServices = Array.from(
    new Set(tableData.map((rate) => rate.service))
  );

  const handleInputChange = (e, service, band, field) => {
    const updatedTableData = tableData.map((rate) => {
      if (rate.service === service && rate.band === band) {
        return { ...rate, [field]: e.target.value };
      }
      return rate;
    });
    setTableData(updatedTableData);
    onTableChange({ ...table, data: updatedTableData });
  };

  const handleServiceChange = (e, oldService) => {
    const newService = e.target.value;
    const updatedTableData = tableData.map((rate) => {
      if (rate.service === oldService) {
        return { ...rate, service: newService };
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

  const handleBandClick = (index) => {
    setActiveBandIndex(index);
  };

  const handleBandBlur = () => {
    setActiveBandIndex(null);
  };

  const handleServiceClick = (index) => {
    setActiveServiceIndex(index);
  };

  const handleServiceBlur = () => {
    setActiveServiceIndex(null);
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
                <TableHead className="w-[360px]">Service</TableHead>
                <TableHead className="text-center">Land/Zone</TableHead>
                {bands.map((value, index) => (
                  <TableHead key={index} className="text-center min-w-[80px]">
                    <div className="flex flex-col items-center">
                      {activeBandIndex === index ? (
                        <textarea
                          value={value}
                          onChange={(e) => handleBandChange(e, index)}
                          onBlur={handleBandBlur}
                          className="bg-transparent border-none text-gray-300 w-full text-center h-12 leading-tight resize-none"
                          autoFocus
                          style={{ height: '3rem', width: '100%' }}
                        />
                      ) : (
                        <span
                          className="whitespace-pre-wrap cursor-pointer"
                          onClick={() => handleBandClick(index)}
                          style={{ height: '3rem', width: '100%' }}
                        >
                          {value}
                        </span>
                      )}
                    </div>
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {uniqueServices.map((service, serviceIndex) => {
                const serviceData = tableData.filter(
                  (rate) => rate.service === service
                );
                return (
                  <TableRow key={service}>
                    <TableCell className="font-medium">
                      {activeServiceIndex === serviceIndex ? (
                        <textarea
                          value={service}
                          onChange={(e) => handleServiceChange(e, service)}
                          onBlur={handleServiceBlur}
                          className="bg-transparent border-none text-gray-300 w-full text-center h-12 leading-tight resize-none"
                          autoFocus
                          style={{ height: '3rem', width: '100%' }}
                        />
                      ) : (
                        <span
                          className="whitespace-pre-wrap cursor-pointer"
                          onClick={() => handleServiceClick(serviceIndex)}
                          style={{ height: '3rem', width: '100%' }}
                        >
                          {service}
                        </span>
                      )}
                    </TableCell>
                    <TableCell className="text-center">
                      <input
                        type="text"
                        value={serviceData[0]["land/zone"]}
                        onChange={(e) => handleInputChange(e, service, null, 'land/zone')}
                        className="bg-transparent border-none text-gray-300 w-full text-center"
                      />
                    </TableCell>
                    {bands.map((band) => {
                      const bandData = serviceData.filter(
                        (rate) => rate.band === band
                      );
                      return (
                        <TableCell key={band} className="text-center">
                          <input
                            type="text"
                            value={bandData.length > 0 ? bandData[0].incentive : ""}
                            onChange={(e) => handleInputChange(e, service, band, 'incentive')}
                            className="bg-transparent border-none text-gray-300 w-full text-center"
                          />
                        </TableCell>
                      );
                    })}
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
