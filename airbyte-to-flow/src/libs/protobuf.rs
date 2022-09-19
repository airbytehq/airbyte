use byteorder::{ByteOrder, LittleEndian};
use bytes::{BufMut, Bytes, BytesMut};
use prost::Message;
use tokio::io::{AsyncRead, AsyncReadExt};

pub async fn decode_message<
    T: Message + std::default::Default,
    R: AsyncRead + std::marker::Unpin,
>(
    reader: &mut R,
) -> Result<Option<T>, std::io::Error> {
    let mut length_buf: [u8; 4] = [0; 4];

    match reader.read_exact(&mut length_buf).await {
        Err(e) => match e.kind() {
            // By the current communication protocol, UnexpectedEof indicates the ending of the stream.
            std::io::ErrorKind::UnexpectedEof => return Ok(None),
            _ => return Err(e),
        },
        Ok(_) => {}
    }

    let message_length = LittleEndian::read_u32(&length_buf);
    let mut message_buf: Vec<u8> = vec![0; message_length as usize];
    reader.read_exact(&mut message_buf).await?;

    Ok(Some(T::decode(&message_buf[..])?))
}

pub fn encode_message<T: Message>(message: &T) -> Result<Bytes, std::io::Error> {
    let mut message_buf: Vec<u8> = Vec::new();
    message.encode(&mut message_buf)?;

    let mut buf_len = [0; 4];
    LittleEndian::write_u32(&mut buf_len, message_buf.len() as u32);

    let mut output_buf = BytesMut::with_capacity(4 + message_buf.len());
    output_buf.put_slice(&buf_len);
    output_buf.put_slice(&message_buf);
    Ok(output_buf.into())
}
