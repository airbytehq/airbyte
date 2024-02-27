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

const CloudProvider: React.FC<IProps> = ({
  setCloudProvider,
  cloudProvider,
  handleInstanceSelect,
  regions,
  setCloudItemId,
  setSelectedRegion,
  setSelectedInstance,
}) => {
  return (
    <CardContainer>
      <Grid container spacing={2}>
        <Grid item lg={12} md={12} sm={12} xs={12}>
          <Box pl={1}>
            <Title>
              <FormattedMessage id="plan.cloudProvider" />
            </Title>
          </Box>
        </Grid>

        <Grid item lg={6} md={6} sm={6} xs={6}>
          <Box pt={2} pl={1}>
            <FormControl>
              <RadioGroup row aria-labelledby="demo-row-radio-buttons-group-label" name="AWS">
                <FormControlLabel
                  value="AWS"
                  control={
                    <Radio
                      onChange={(e) => {
                        // setIsCloud(true);
                        setCloudProvider(e.target.value);
                        setCloudItemId(regions[0]?.cloudItemId);
                        handleInstanceSelect(regions[0]?.cloudItemId);
                      }}
                      sx={{
                        "&.Mui-checked": {
                          color: "#4F46E5",
                        },
                      }}
                      checked={cloudProvider === "AWS"}
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
                      <FormattedMessage id="plan.aws" />
                    </span>
                  }
                />
              </RadioGroup>
            </FormControl>
          </Box>
        </Grid>

        <Grid item lg={6} md={6} sm={6} xs={6}>
          {regions?.find(
            (region: any) =>
              region?.cloudProviderName === "GOOGLE CLOUD" && (
                <Box pt={2} pl={1}>
                  <FormControl>
                    <RadioGroup row aria-labelledby="demo-row-radio-buttons-group-label" name="GOOGLE CLOUD">
                      <FormControlLabel
                        value="GOOGLE CLOUD"
                        control={
                          <Radio
                            onChange={(e) => {
                              // setIsCloud(true);
                              setCloudProvider(e.target.value);
                              setSelectedRegion("");
                              setSelectedInstance("");
                              setCloudItemId(regions[1]?.cloudItemId);
                              handleInstanceSelect(regions[1]?.cloudItemId);
                              // setInstanceSelected(false);
                            }}
                            sx={{
                              "&.Mui-checked": {
                                color: "#4F46E5",
                              },
                            }}
                            checked={cloudProvider === "GOOGLE CLOUD"}
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
                            <FormattedMessage id="plan.gcp" />
                          </span>
                        }
                      />
                    </RadioGroup>
                  </FormControl>
                </Box>
              )
          )}
        </Grid>
      </Grid>
    </CardContainer>
  );
};

export default CloudProvider;
