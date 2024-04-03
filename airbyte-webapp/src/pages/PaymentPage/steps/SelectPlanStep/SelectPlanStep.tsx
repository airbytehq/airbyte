import _ from "lodash";
import React from "react";

import { Separator } from "components/Separator";

import { ProcessedPackageMap, ProductItem, ProductOptionItem } from "core/domain/product";

import CloudProvider from "./components/CloudProvider";
import DeploymentMode from "./components/DeploymentMode";
import FeaturesCard from "./components/FeaturesCard";
import Instance from "./components/Instance";
import Region from "./components/Region";
// import FeatureNot from "./components/FeatureNot";

interface IProps {
  product?: ProductOptionItem;
  setProduct?: (item: ProductOptionItem) => void;
  selectedProduct?: ProductItem;
  paymentLoading: boolean;
  productOptions?: ProductOptionItem[];
  packagesMap: ProcessedPackageMap;
  onSelectPlan?: () => void;
  deploymentMode?: string;
  setDeploymentMode?: any;
  setCloudProvider?: any;
  cloudProvider?: string;
  mode?: boolean;
  setMode?: any;
  regions?: any;
  handleInstanceSelect?: any;
  setCloudItemId?: any;
  cloudItemId?: string;
  setSelectedRegion?: any;
  setSelectedInstance?: any;
  selectedRegion?: string;
  selectedInstance?: string;
  instance?: any;
  packages?: any;
  setCloudPackageId?: any;
  setPrice?: any;
  price?: any;
  planDetail?: any;
  setInstanceSelected?: any;
  instanceSelected?: boolean;
  jobs?: any;
  setJobs?: any;
  setIsCloud?: any;
  cloudRef?: any;
  setRegionSelected?: any;
  regionScrollRef?: any;
  instanceRef?: any;
  isCloud?: boolean;
  regionSelected?: boolean;
  user?: any;
}

const SelectPlanStep: React.FC<IProps> = ({
  product,
  selectedProduct,
  paymentLoading,
  packagesMap,
  setDeploymentMode,
  deploymentMode,
  setMode,
  mode,
  setCloudProvider,
  setIsCloud,
  cloudProvider,
  regions,
  onSelectPlan,
  handleInstanceSelect,
  setCloudItemId,
  cloudItemId,
  setSelectedRegion,
  setSelectedInstance,
  instance,
  packages,
  selectedRegion,
  selectedInstance,
  setCloudPackageId,
  setPrice,
  price,
  planDetail,
  setInstanceSelected,
  instanceSelected,
  jobs,
  setJobs,
  cloudRef,
  regionScrollRef,
  setRegionSelected,
  instanceRef,
  isCloud,
  regionSelected,
  user,
}) => {
  return (
    <>
      <DeploymentMode
        selectedProduct={selectedProduct}
        deploymentMode={deploymentMode}
        setDeploymentMode={setDeploymentMode}
        mode={mode}
        setMode={setMode}
      />
      <Separator height="30px" />
      <CloudProvider
        setCloudProvider={setCloudProvider}
        cloudProvider={cloudProvider}
        regions={regions}
        handleInstanceSelect={handleInstanceSelect}
        cloudItemId={cloudItemId}
        setCloudItemId={setCloudItemId}
        setSelectedInstance={setSelectedInstance}
        setSelectedRegion={setSelectedRegion}
        setIsCloud={setIsCloud}
      />
      <Separator height="30px" />
      {isCloud && (
        <Region
          instance={instance}
          regions={regions}
          setSelectedRegion={setSelectedRegion}
          setSelectedInstance={setSelectedInstance}
          selectedRegion={selectedRegion}
          cloudProvider={cloudProvider}
          setPrice={setPrice}
          selectedProduct={selectedProduct}
          setInstanceSelected={setInstanceSelected}
          cloudItemId={cloudItemId}
          cloudRef={cloudRef}
          setRegionSelected={setRegionSelected}
        />
      )}

      <Separator height="30px" />
      {regionSelected && (
        <Instance
          packages={packages}
          selectedInstance={selectedInstance}
          instance={instance}
          cloudItemId={cloudItemId}
          setCloudPackageId={setCloudPackageId}
          setPrice={setPrice}
          // selectedProduct={selectedProduct}
          setSelectedInstance={setSelectedInstance}
          selectedRegion={selectedRegion}
          instanceSelected={instanceSelected}
          regionScrollRef={regionScrollRef}
          setInstanceSelected={setInstanceSelected}
          setJobs={setJobs}
        />
      )}

      <Separator height="30px" />
      {instanceSelected && price !== "" ? (
        <FeaturesCard
          product={product}
          instanceRef={instanceRef}
          selectPlanBtnDisability={_.isEqual(product?.id, selectedProduct?.id)}
          onSelectPlan={onSelectPlan}
          paymentLoading={paymentLoading}
          packagesMap={packagesMap}
          price={price}
          planDetail={planDetail}
          selectedProduct={selectedProduct}
          jobs={jobs}
          user={user}
        />
      ) : null}
    </>
  );
};

export default SelectPlanStep;
