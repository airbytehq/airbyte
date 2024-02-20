import { Box, FormControl, FormControlLabel, Grid, Radio, RadioGroup } from "@mui/material";
import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { ProductOptionItem } from "core/domain/product";

interface IProps {
  productOptions?: ProductOptionItem[];
  product?: ProductOptionItem;
  setProduct?: (item: ProductOptionItem) => void;
  selectedProduct?: any;
  mode?: boolean;
  setCloudProvider?: any;
  cloudProvider?: string;
  handleInstanceSelect?: any;
  regions?: any;
  cloudItemId?: string;
  setCloudItemId?: any;
  setSelectedRegion?: any;
  setSelectedInstance?: any;
  selectedRegion?: any;
  instance?: any;
  setInstanceSelected?: any;
  setPrice?: any;
}

const Title = styled.div`
  font-weight: 500;
  font-size: 18px;
  line-height: 30px;
  color: ${({ theme }) => theme.black300};
  user-select: none;
`;

// const DeployContainer = styled.div`
//   padding: 50px;
// `;

const CardContainer = styled.div`
  padding: 20px 20px;
  background: #ffffff;
  border-radius: 16px;
`;

const Region: React.FC<IProps> = ({
  regions,
  setSelectedRegion,
  setSelectedInstance,
  cloudProvider,
  selectedRegion,
  selectedProduct,
  setPrice,
  setInstanceSelected,
}) => {
  return (
    <CardContainer>
      <Grid container spacing={2}>
        <Grid item lg={12} md={12} sm={12} xs={12}>
          <Box pl={1}>
            <Title>
              <FormattedMessage id="plan.cloudRegion" />
            </Title>
          </Box>
        </Grid>

        {regions[0]?.cloudProviderName === "AWS" &&
          cloudProvider === "AWS" &&
          regions[0]?.regionList.map((region: any) => {
            return (
              <Grid item lg={3} md={3} sm={6} xs={12} key={region?.regionItemId}>
                <Box pt={2} pl={{ lg: 1 }}>
                  <FormControl>
                    <RadioGroup row aria-labelledby="demo-row-radio-buttons-group-label" name={region?.region}>
                      <FormControlLabel
                        value={region?.regionItemId}
                        control={
                          <Radio
                            onChange={(e) => {
                              setSelectedRegion(e.target.value);
                              setSelectedInstance("");
                              // setRegionSelected(true);
                              setPrice("");
                            }}
                            sx={{
                              "&.Mui-checked": {
                                color: "#4F46E5",
                              },
                              "&.Mui-disabled": {
                                color: "#AAAAAA",
                              },
                            }}
                            checked={selectedRegion === region?.regionItemId}
                            disabled={
                              selectedProduct?.regionItemId === region?.regionItemId &&
                              selectedProduct?.regionItemId === selectedRegion
                            }
                          />
                        }
                        label={
                          <span
                            style={{
                              fontSize: "14px",
                              whiteSpace: "nowrap",
                              overflow: "hidden",
                              textOverflow: "ellipsis",
                            }}
                          >
                            {region?.region}
                          </span>
                        }
                      />
                    </RadioGroup>
                  </FormControl>
                </Box>
              </Grid>
            );
          })}
        {regions[1]?.cloudProviderName === "GOOGLE CLOUD" &&
          cloudProvider === "GOOGLE CLOUD" &&
          regions[1]?.regionList.map((region: any) => {
            return (
              <Grid item lg={3} md={3} sm={6} xs={12} key={region?.regionItemId} pl={1}>
                <Box pt={2}>
                  <FormControl>
                    <RadioGroup row aria-labelledby="demo-row-radio-buttons-group-label" name={region?.region}>
                      <FormControlLabel
                        value={region?.regionItemId}
                        control={
                          <Radio
                            onChange={(e) => {
                              setSelectedRegion(e.target.value);
                              setSelectedInstance("");
                              setInstanceSelected(true);
                              // setRegionSelected(true);
                            }}
                            sx={{
                              "&.Mui-checked": {
                                color: "#4F46E5",
                              },
                              "&.Mui-disabled": {
                                color: "#AAAAAA",
                              },
                            }}
                            checked={selectedRegion === region?.regionItemId}
                            disabled={selectedProduct?.regionItemId === region?.regionItemId}
                          />
                        }
                        label={
                          <span
                            style={{
                              fontSize: "14px",
                              whiteSpace: "nowrap",
                              overflow: "hidden",
                              textOverflow: "ellipsis",
                            }}
                          >
                            {region?.region}
                          </span>
                        }
                      />
                    </RadioGroup>
                  </FormControl>
                </Box>
              </Grid>
            );
          })}
      </Grid>
    </CardContainer>
  );
};

export default Region;
