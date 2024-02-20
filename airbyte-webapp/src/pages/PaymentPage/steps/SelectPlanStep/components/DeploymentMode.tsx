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
  setMode?: any;
  setDeploymentMode?: any;
  deploymentMode?: any;
}
const TitleB = styled.div`
  font-weight: 400;
  font-size: 16px;
  line-height: 30px;
  color: #999999;
  user-select: none;
`;
const Title = styled.div`
  font-weight: 500;
  font-size: 18px;
  line-height: 30px;
  color: ${({ theme }) => theme.black300};
  user-select: none;
`;

const CardContainer = styled.div`
  padding: 20px 20px;
  background: #ffffff;
  border-radius: 16px;
`;

const DeploymentMode: React.FC<IProps> = ({ selectedProduct, setDeploymentMode, deploymentMode, setMode }) => {
  //   const valueLabelFormat = (value: any) => {
  //     return productOptions.findIndex((option) => option.value === value) + 1;
  //   };

  //   const getSinglePrice = (event: any) => {
  //     const matchingOptions = productOptions.filter((option) => {
  //       return option.value === event.target.value;
  //     });
  //     setProduct(matchingOptions[0]);
  //   };

  return (
    <CardContainer>
      <Grid container spacing={2}>
        <Grid item lg={12} md={12} sm={12} xs={12}>
          <Box pl={1}>
            <Title>
              <FormattedMessage id="plan.preferredMode" />
            </Title>
          </Box>

          <Box pt={2} pl={1}>
            <FormControl>
              <RadioGroup row aria-labelledby="demo-row-radio-buttons-group-label" name="fully-managed">
                <FormControlLabel
                  value="fully"
                  control={
                    <Radio
                      onChange={(e) => {
                        setDeploymentMode(e.target.value);
                        setMode(true);
                      }}
                      sx={{
                        "&.Mui-checked": {
                          color: "#4F46E5",
                        },
                      }}
                      checked={deploymentMode === "fully" || selectedProduct?.cloudProviderName === "AWS"}
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
                      <FormattedMessage id="plan.fullyManaged" />
                    </span>
                  }
                />
              </RadioGroup>
            </FormControl>
            <Box pl={4}>
              <TitleB>
                {}
                <FormattedMessage id="plan.fullmanage" />
                <br /> <FormattedMessage id="plan.fullnext" />
              </TitleB>
            </Box>
          </Box>
        </Grid>
      </Grid>
    </CardContainer>
  );
};

export default DeploymentMode;
