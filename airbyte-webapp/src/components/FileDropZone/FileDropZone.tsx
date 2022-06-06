import { faFile } from "@fortawesome/free-regular-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { DropzoneOptions, useDropzone } from "react-dropzone";
import styled from "styled-components";

const Content = styled.div<{ hasFiles: boolean }>`
  width: 100%;
  outline: none;
  padding: 12px 10px;
  border-radius: 4px;
  font-size: 14px;
  line-height: 20px;
  font-weight: normal;
  border: 1px solid ${({ theme, hasFiles }) => (hasFiles ? theme.primaryColor : theme.greyColor0)};
  background: ${({ theme, hasFiles }) => (hasFiles ? theme.primaryColor12 : theme.greyColor0)};
  color: ${({ theme }) => theme.greyColor40};
  cursor: pointer;
  min-height: 95px;
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;

  &:hover {
    background: ${({ theme }) => theme.greyColor20};
    border-color: ${({ theme }) => theme.greyColor20};
  }

  &:active {
    border-color: ${({ theme }) => theme.primaryColor};
  }

  &:disabled {
    pointer-events: none;
    background: ${({ theme }) => theme.greyColor55};
  }
`;

const FileView = styled.div`
  color: ${({ theme }) => theme.textColor};

  &:first-child {
    margin-top: 7px;
  }
`;

const FileIcon = styled(FontAwesomeIcon)`
  font-size: 16px;
  margin-right: 8px;
`;

interface IProps {
  className?: string;
  mainText?: React.ReactNode;
  options?: DropzoneOptions;
}

const FileDropZone: React.FC<IProps> = ({ className, mainText, options }) => {
  const { acceptedFiles, getRootProps, getInputProps } = useDropzone(options);

  return (
    <Content {...getRootProps({ className: `dropzone ${className}` })} hasFiles={!!acceptedFiles.length}>
      <input {...getInputProps()} />
      {mainText}
      <div>
        {acceptedFiles.map((file, index) => (
          <FileView key={index}>
            <FileIcon icon={faFile} />
            {file.name}
          </FileView>
        ))}
      </div>
    </Content>
  );
};

export default FileDropZone;
