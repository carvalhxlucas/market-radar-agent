import jsPDF from 'jspdf';

interface ExtractedDataItem {
  prices?: Array<{ value: number; currency: string } | number>;
  product_names?: string[];
  url?: string;
  title?: string;
  average_price?: number;
  currency?: string;
  timestamp?: string;
}

interface ExportData {
  goal: string;
  data: ExtractedDataItem[];
  sources: Array<{ url: string; title?: string }>;
  summary?: string;
}

export async function exportToPDF(exportData: ExportData): Promise<void> {
  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  let yPosition = 20;

  doc.setFontSize(18);
  doc.setTextColor(200, 200, 200);
  doc.text('MarketRadar - Research Report', pageWidth / 2, yPosition, { align: 'center' });
  yPosition += 15;

  doc.setFontSize(12);
  doc.setTextColor(180, 180, 180);
  doc.text(`Goal: ${exportData.goal}`, 20, yPosition);
  yPosition += 10;

  if (exportData.summary) {
    doc.setFontSize(10);
    const summaryLines = doc.splitTextToSize(exportData.summary, pageWidth - 40);
    doc.text(summaryLines, 20, yPosition);
    yPosition += summaryLines.length * 5 + 10;
  }

  if (exportData.data.length > 0) {
    doc.setFontSize(14);
    doc.setTextColor(200, 200, 200);
    doc.text('Extracted Data', 20, yPosition);
    yPosition += 10;

    exportData.data.forEach((item, index) => {
      if (yPosition > pageHeight - 40) {
        doc.addPage();
        yPosition = 20;
      }

      doc.setFontSize(12);
      doc.setTextColor(200, 200, 200);
      doc.text(`Record ${index + 1}`, 20, yPosition);
      yPosition += 8;

      if (item.title) {
        doc.setFontSize(10);
        doc.text(`Title: ${item.title}`, 25, yPosition);
        yPosition += 6;
      }

      if (item.url) {
        doc.setFontSize(9);
        doc.setTextColor(150, 150, 150);
        doc.text(`URL: ${item.url}`, 25, yPosition);
        yPosition += 6;
        doc.setTextColor(200, 200, 200);
      }

      if (item.prices && item.prices.length > 0) {
        doc.setFontSize(10);
        doc.text(`Prices found (${item.prices.length}):`, 25, yPosition);
        yPosition += 6;
        
        item.prices.forEach((price) => {
          const value = typeof price === 'object' ? price.value : price;
          const currency = typeof price === 'object' ? price.currency : 'BRL';
          doc.setFontSize(9);
          doc.text(`  • ${currency === 'BRL' ? 'R$' : currency} ${value.toFixed(2)}`, 30, yPosition);
          yPosition += 5;
        });
      }

      if (item.average_price) {
        doc.setFontSize(10);
        doc.setTextColor(180, 180, 180);
        doc.text(`Average: R$ ${item.average_price.toFixed(2)}`, 25, yPosition);
        yPosition += 8;
        doc.setTextColor(200, 200, 200);
      }

      yPosition += 5;
    });
  }

  if (exportData.sources.length > 0) {
    if (yPosition > pageHeight - 60) {
      doc.addPage();
      yPosition = 20;
    }

    doc.setFontSize(14);
    doc.setTextColor(200, 200, 200);
    doc.text('Consulted Sources', 20, yPosition);
    yPosition += 10;

    exportData.sources.forEach((source) => {
      if (yPosition > pageHeight - 40) {
        doc.addPage();
        yPosition = 20;
      }

      doc.setFontSize(10);
      doc.setTextColor(200, 200, 200);
      if (source.title) {
        doc.text(source.title, 25, yPosition);
        yPosition += 6;
      }
      doc.setFontSize(9);
      doc.setTextColor(150, 150, 150);
      const urlLines = doc.splitTextToSize(source.url, pageWidth - 50);
      doc.text(urlLines, 25, yPosition);
      yPosition += urlLines.length * 5 + 5;
    });
  }

  doc.save(`marketradar-report-${new Date().toISOString().split('T')[0]}.pdf`);
}
