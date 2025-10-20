import React, { useEffect, useRef, useState } from 'react';
import { Card, Button, InputNumber, Space, Typography, Switch, Alert, Divider } from 'antd';
import { EnvironmentOutlined, EditOutlined, GlobalOutlined } from '@ant-design/icons';

const { Text } = Typography;

// Utility function to round coordinates to 6 decimal places (backend validation requirement)
const roundToSixDecimals = (value) => {
  return value ? Math.round(value * 1000000) / 1000000 : value;
};

const YandexMapPicker = ({ 
  latitude, 
  longitude, 
  onLatitudeChange, 
  onLongitudeChange,
  height = 400 
}) => {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const placemarkRef = useRef(null);
  const [isMapLoaded, setIsMapLoaded] = useState(false);
  const [useMapMode, setUseMapMode] = useState(true);
  const [mapError, setMapError] = useState(null);
  const [manualLatitude, setManualLatitude] = useState(latitude);
  const [manualLongitude, setManualLongitude] = useState(longitude);

  // Load Yandex Maps API
  useEffect(() => {
    const apiKey = import.meta.env.VITE_YANDEX_MAPS_API_KEY || 'YOUR_YANDEX_API_KEY';
    
    // Check if API key is properly configured
    if (apiKey === 'YOUR_YANDEX_API_KEY' || !apiKey) {
      setMapError('Yandex Maps API key not configured. Please add VITE_YANDEX_MAPS_API_KEY to your .env file.');
      setUseMapMode(false);
      return;
    }

    const script = document.createElement('script');
    script.src = `https://api-maps.yandex.ru/2.1/?apikey=${apiKey}&lang=en_US`;
    script.async = true;
    script.onload = () => {
      window.ymaps.ready(() => {
        setIsMapLoaded(true);
        setMapError(null);
      });
    };
    script.onerror = () => {
      setMapError('Failed to load Yandex Maps API. Please check your internet connection and API key.');
      setUseMapMode(false);
    };
    document.head.appendChild(script);

    return () => {
      if (document.head.contains(script)) {
        document.head.removeChild(script);
      }
    };
  }, []);

  // Initialize map when API is loaded
  useEffect(() => {
    if (!isMapLoaded || !mapRef.current) return;

    const initMap = () => {
      // Default coordinates (Moscow if no coordinates provided)
      const defaultLat = latitude || 55.7558;
      const defaultLon = longitude || 37.6176;

      mapInstanceRef.current = new window.ymaps.Map(mapRef.current, {
        center: [defaultLat, defaultLon],
        zoom: 10,
        controls: ['zoomControl', 'searchControl', 'typeSelector', 'fullscreenControl']
      });

      // Add placemark
      placemarkRef.current = new window.ymaps.Placemark([defaultLat, defaultLon], {
        balloonContent: 'Selected location'
      }, {
        draggable: true
      });

      mapInstanceRef.current.geoObjects.add(placemarkRef.current);

      // Handle placemark drag
      placemarkRef.current.events.add('dragend', () => {
        const coords = placemarkRef.current.geometry.getCoordinates();
        const roundedLat = roundToSixDecimals(coords[0]);
        const roundedLon = roundToSixDecimals(coords[1]);
        onLatitudeChange(roundedLat);
        onLongitudeChange(roundedLon);
        // Update manual inputs
        setManualLatitude(roundedLat);
        setManualLongitude(roundedLon);
      });

      // Handle map click
      mapInstanceRef.current.events.add('click', (e) => {
        const coords = e.get('coords');
        const roundedLat = roundToSixDecimals(coords[0]);
        const roundedLon = roundToSixDecimals(coords[1]);
        placemarkRef.current.geometry.setCoordinates([roundedLat, roundedLon]);
        onLatitudeChange(roundedLat);
        onLongitudeChange(roundedLon);
        // Update manual inputs
        setManualLatitude(roundedLat);
        setManualLongitude(roundedLon);
      });
    };

    initMap();

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.destroy();
      }
    };
  }, [isMapLoaded, latitude, longitude, onLatitudeChange, onLongitudeChange]);

  // Update map center when coordinates change externally
  useEffect(() => {
    if (mapInstanceRef.current && placemarkRef.current && latitude && longitude) {
      const roundedLat = roundToSixDecimals(latitude);
      const roundedLon = roundToSixDecimals(longitude);
      const coords = [roundedLat, roundedLon];
      mapInstanceRef.current.setCenter(coords, 15);
      placemarkRef.current.geometry.setCoordinates(coords);
    }
  }, [latitude, longitude]);

  const handleCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const coords = [position.coords.latitude, position.coords.longitude];
          const roundedLat = roundToSixDecimals(coords[0]);
          const roundedLon = roundToSixDecimals(coords[1]);
          if (mapInstanceRef.current && placemarkRef.current) {
            mapInstanceRef.current.setCenter([roundedLat, roundedLon], 15);
            placemarkRef.current.geometry.setCoordinates([roundedLat, roundedLon]);
            onLatitudeChange(roundedLat);
            onLongitudeChange(roundedLon);
          }
          // Also update manual inputs
          setManualLatitude(roundedLat);
          setManualLongitude(roundedLon);
        },
        (error) => {
          console.error('Error getting current location:', error);
        }
      );
    }
  };

  const handleManualLatitudeChange = (value) => {
    // Round to 6 decimal places to match backend validation
    const roundedValue = roundToSixDecimals(value);
    setManualLatitude(roundedValue);
    onLatitudeChange(roundedValue);
  };

  const handleManualLongitudeChange = (value) => {
    // Round to 6 decimal places to match backend validation
    const roundedValue = roundToSixDecimals(value);
    setManualLongitude(roundedValue);
    onLongitudeChange(roundedValue);
  };

  const handleModeToggle = (checked) => {
    setUseMapMode(checked);
    if (!checked) {
      // Switching to manual mode - sync current values and round them
      const roundedLat = roundToSixDecimals(latitude);
      const roundedLon = roundToSixDecimals(longitude);
      setManualLatitude(roundedLat);
      setManualLongitude(roundedLon);
    }
  };

  return (
    <div>
      <Card 
        title={
          <Space>
            <EnvironmentOutlined />
            <Text>Select Location</Text>
          </Space>
        }
        extra={
          <Space>
            <Switch
              checkedChildren={<GlobalOutlined />}
              unCheckedChildren={<EditOutlined />}
              checked={useMapMode}
              onChange={handleModeToggle}
              disabled={!!mapError}
            />
            <Text type="secondary" style={{ fontSize: 12 }}>
              {useMapMode ? 'Map Mode' : 'Manual Mode'}
            </Text>
            {useMapMode && (
              <Button 
                type="primary" 
                size="small" 
                onClick={handleCurrentLocation}
                disabled={!isMapLoaded}
              >
                Use Current Location
              </Button>
            )}
          </Space>
        }
        style={{ marginBottom: 16 }}
      >
        {mapError && (
          <Alert
            message="Map Unavailable"
            description={mapError}
            type="warning"
            showIcon
            style={{ marginBottom: 16 }}
            action={
              <Button size="small" onClick={() => setUseMapMode(false)}>
                Use Manual Input
              </Button>
            }
          />
        )}
        
        {useMapMode && !mapError ? (
          <div 
            ref={mapRef} 
            style={{ 
              width: '100%', 
              height: height,
              borderRadius: 6,
              border: '1px solid #d9d9d9'
            }} 
          />
        ) : (
          <div style={{ padding: '20px 0', textAlign: 'center' }}>
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <EditOutlined style={{ fontSize: 48, color: '#1890ff' }} />
              <Text strong>Manual Coordinate Entry</Text>
              <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                <div style={{ flex: 1, marginRight: 8 }}>
                  <Text strong>Latitude:</Text>
                  <InputNumber
                    value={manualLatitude}
                    onChange={handleManualLatitudeChange}
                    precision={6}
                    style={{ width: '100%', marginTop: 4 }}
                    placeholder="Enter latitude"
                  />
                </div>
                <div style={{ flex: 1, marginLeft: 8 }}>
                  <Text strong>Longitude:</Text>
                  <InputNumber
                    value={manualLongitude}
                    onChange={handleManualLongitudeChange}
                    precision={6}
                    style={{ width: '100%', marginTop: 4 }}
                    placeholder="Enter longitude"
                  />
                </div>
              </Space>
            </Space>
          </div>
        )}
      </Card>
      
      {useMapMode && !mapError && (
        <>
          <Divider />
          <Space style={{ width: '100%', justifyContent: 'space-between' }}>
            <div style={{ flex: 1, marginRight: 8 }}>
              <Text strong>Latitude:</Text>
              <InputNumber
                value={latitude}
                onChange={onLatitudeChange}
                precision={6}
                style={{ width: '100%', marginTop: 4 }}
                placeholder="Enter latitude"
              />
            </div>
            <div style={{ flex: 1, marginLeft: 8 }}>
              <Text strong>Longitude:</Text>
              <InputNumber
                value={longitude}
                onChange={onLongitudeChange}
                precision={6}
                style={{ width: '100%', marginTop: 4 }}
                placeholder="Enter longitude"
              />
            </div>
          </Space>
        </>
      )}
      
      <div style={{ marginTop: 8 }}>
        <Text type="secondary" style={{ fontSize: 12 }}>
          {useMapMode && !mapError 
            ? "Click on the map or drag the marker to select coordinates. You can also manually enter coordinates in the fields above."
            : "Enter coordinates manually. Switch to map mode if available for easier selection."
          }
        </Text>
      </div>
    </div>
  );
};

export default YandexMapPicker;
